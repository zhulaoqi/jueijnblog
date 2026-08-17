# JDBC 核心连接参数说明与 BI 稳定性配置建议

> 本文面向 BI 系统的 JDBC 连接配置，覆盖 **ClickHouse、StarRocks、MySQL** 三类数据源。
>
> 本文的配置目标不是“快失败”，而是：**尽可能保证每一次查询都能稳定返回结果**。
>
> 对 BI 系统来说，用户最不能接受的是：
>
> - 看板偶发打不开
> - 查询偶发 500
> - 连接池偶发拿到坏连接
> - 数据库轻微抖动就直接失败
>
> 所以本文采用 **稳定优先、容忍抖动、后台保活、必要时等待** 的配置思路。

---

## 一、核心原则：BI 查询要稳定，不是快失败

普通在线接口通常强调“快失败”，因为接口请求不能一直卡住。

但 BI 查询不同：

- 查询本身可能就是秒级、十秒级、分钟级
- 数据库可能存在短暂抖动
- 用户更关心“结果能不能出来”
- 部分查询失败后重试成本很高
- 看板加载失败会直接影响用户信任

所以 BI JDBC 配置应遵循以下原则：

| 原则 | 说明 |
|------|------|
| **连接允许适度等待** | 数据库网络短暂抖动时，不要 3 秒就失败 |
| **读取超时要覆盖大部分查询** | `socketTimeout` 应覆盖正常慢查询，而不是过早中断 |
| **连接池要保留足够热连接** | 减少临时建连带来的失败和延迟 |
| **借连接前优先保证连接有效** | 稳定优先时，可以接受 `testOnBorrow=true` 的额外开销 |
| **后台保活必须开启** | 防止 NAT、LB、防火墙、数据库主动清理空闲连接 |
| **慢查询不能无限放大** | 稳定不是无限等待，需要给不同查询类型分池 |

一句话：

> **BI 系统不是追求最快报错，而是追求在合理等待范围内尽量查出来。**

---

## 二、JDBC 查询链路与超时位置

一次 BI 查询会经过以下链路：

```mermaid
flowchart LR
    A["用户发起 BI 查询"] --> B["连接池获取连接<br/>maxWait"]
    B --> C["连接可用性检查<br/>validationQuery"]
    C --> D["建立或复用 TCP 连接<br/>connectTimeout"]
    D --> E["发送 SQL"]
    E --> F["数据库执行查询"]
    F --> G["客户端等待结果<br/>socketTimeout"]
    G --> H["读取结果集"]
    H --> I["归还连接"]

    style B fill:#fef3c7,stroke:#f59e0b,color:#000
    style C fill:#d1fae5,stroke:#10b981,color:#000
    style D fill:#fee2e2,stroke:#ef4444,color:#000
    style G fill:#fee2e2,stroke:#ef4444,color:#000
```

关键参数位置：

| 参数 | 控制阶段 | 稳定性含义 |
|------|----------|------------|
| `maxWait` | 等连接池可用连接 | 高峰时允许排队等待，避免直接失败 |
| `validationQuery` | 校验连接 | 避免拿到已断开的连接 |
| `connectTimeout` | 建立 TCP 连接 | 网络短暂抖动时允许一定恢复时间 |
| `socketTimeout` | 等待数据库响应/读取结果 | 覆盖慢查询，避免结果未返回就断开 |
| `queryTimeout` | SQL 执行时间 | 控制 SQL 本身最长执行时间 |

---

## 三、当前配置解读

当前 ClickHouse JDBC 示例：

```text
jdbc:clickhouse://10.102.133.221:8123/?socketTimeout=300000&connectTimeout=300000
```

连接池参数：

| 参数 | 当前值 |
|------|--------|
| `minIdle` | 20 |
| `validationQuery` | `select 1` |
| `keepAlive` | true |
| `initialSize` | 20 |
| `maxWait` | 10000 |
| `useUnfairLock` | true |
| `testOnBorrow` | false |
| `testWhileIdle` | true |
| `minEvictableIdleTimeMillis` | 120000 |
| `timeBetweenEvictionRunsMillis` | 6000 |
| `testOnReturn` | false |
| `maxEvictableIdleTimeMillis` | 600000 |
| `maxActive` | 40 |

这组配置的优点：

- `initialSize=20`、`minIdle=20`：预热连接较多，对 BI 看板友好
- `maxActive=40`：能支撑中等并发
- `keepAlive=true`：方向正确，有助于长连接稳定
- `testWhileIdle=true`：后台检测连接，能减少死连接
- `socketTimeout=300000`：允许 5 分钟查询，对复杂分析相对友好

需要调整的点：

| 参数 | 当前问题 | 建议方向 |
|------|----------|----------|
| `connectTimeout=300000` | 建连等待 5 分钟过长，故障时线程会被长时间挂住 | 稳定场景建议 30000~60000 ms |
| `maxWait=10000` | 高峰时等连接最多 10 秒，可能偏短 | 稳定优先建议 30000 ms |
| `testOnBorrow=false` | 极端情况下可能借到刚失效的连接 | 稳定优先建议 true，或配合失败重试 |
| `timeBetweenEvictionRunsMillis=6000` | 每 6 秒巡检一次，偏频繁 | 建议 30000 ms，配合 keepAlive |
| `minEvictableIdleTimeMillis=120000` | 空闲 2 分钟即可能回收，热连接保留时间偏短 | 建议 300000~600000 ms |

---

## 四、网络参数建议

### 4.1 `connectTimeout`

**含义**：建立 TCP 连接的最长等待时间。

如果数据库短暂网络抖动、DNS 抖动、LB 抖动，`connectTimeout` 太短会导致大量偶发连接失败。

BI 稳定优先建议：

| 场景 | 建议值 |
|------|--------|
| 同机房 / 内网 | 10000 ~ 30000 ms |
| 跨机房 / 跨地域 | 30000 ~ 60000 ms |
| 高稳定兜底 | 60000 ms |
| 不建议 | 300000 ms |

为什么不建议 300000？

不是因为要快失败，而是因为建连失败通常意味着网络或数据库不可达。等待 5 分钟会占住业务线程、连接池线程和请求上下文，容易造成级联阻塞。  

**稳定优先不是无限等待，而是给网络抖动足够恢复时间。**

### 4.2 `socketTimeout`

**含义**：连接建立后，等待数据库响应或读取结果的最长时间。

BI 稳定优先建议：

| 查询类型 | 建议值 |
|----------|--------|
| 普通看板查询 | 180000 ~ 300000 ms |
| 复杂分析查询 | 300000 ~ 600000 ms |
| 导出 / 大报表 | 600000 ~ 1800000 ms |

对于 BI 系统，`socketTimeout=300000` 是可以接受的基础值，尤其是 ClickHouse / StarRocks 这种 OLAP 查询。

如果业务要求“每次尽量查出来”，建议：

- 看板查询：`socketTimeout=300000`
- 复杂查询：`socketTimeout=600000`
- 导出查询：`socketTimeout=1800000`

### 4.3 `queryTimeout`

**含义**：SQL 执行层面的超时。

建议 `socketTimeout` 大于 `queryTimeout`：

```text
queryTimeout = 240s
socketTimeout = 300s
```

这样数据库有机会主动结束 SQL，而不是客户端 socket 先断。

BI 稳定建议：

| 查询类型 | `queryTimeout` | `socketTimeout` |
|----------|----------------|-----------------|
| 普通看板 | 180~240 秒 | 300 秒 |
| 复杂分析 | 300~480 秒 | 600 秒 |
| 导出任务 | 900~1500 秒 | 1800 秒 |

---

## 五、连接池参数建议

以下以 Druid 风格参数为主。

### 5.1 容量参数

| 参数 | 当前值 | 稳定优先建议 | 说明 |
|------|--------|--------------|------|
| `initialSize` | 20 | 20 | 启动时预热连接，减少首次查询失败 |
| `minIdle` | 20 | 20 | 保留热连接，适合 BI 高频查询 |
| `maxActive` | 40 | 40~80 | 根据数据库承载能力调整 |
| `maxWait` | 10000 | 30000 | 高峰时允许等待连接，减少直接失败 |

建议：

```properties
initialSize=20
minIdle=20
maxActive=40
maxWait=30000
```

如果 BI 并发较高：

```properties
initialSize=20
minIdle=20
maxActive=60
maxWait=30000
```

注意：`maxActive` 不是越大越好。它需要结合数据库最大连接数、查询并发能力、CPU/内存资源一起评估。

### 5.2 连接有效性检测

| 参数 | 当前值 | 稳定优先建议 | 说明 |
|------|--------|--------------|------|
| `validationQuery` | `select 1` | `select 1` | 保持 |
| `testOnBorrow` | false | true | 借连接前校验，避免死连接 |
| `testOnReturn` | false | false | 归还时无需检测 |
| `testWhileIdle` | true | true | 后台检测空闲连接 |
| `keepAlive` | true | true | 空闲连接保活 |

稳定优先建议：

```properties
validationQuery=select 1
testOnBorrow=true
testOnReturn=false
testWhileIdle=true
keepAlive=true
```

为什么建议 `testOnBorrow=true`？

因为 BI 更关注“拿到的连接一定能用”。  

`testOnBorrow=true` 会增加一次 `select 1` 的开销，但可以显著降低拿到坏连接后首个查询失败的概率。

如果后续确认 `select 1` 开销过大，可以改为：

```properties
testOnBorrow=false
testWhileIdle=true
keepAlive=true
```

同时在应用层增加“连接异常自动重试一次”。

### 5.3 空闲连接巡检与回收

| 参数 | 当前值 | 稳定优先建议 | 说明 |
|------|--------|--------------|------|
| `timeBetweenEvictionRunsMillis` | 6000 | 30000 | 每 30 秒巡检一次 |
| `minEvictableIdleTimeMillis` | 120000 | 300000~600000 | 空闲 5~10 分钟后允许回收 |
| `maxEvictableIdleTimeMillis` | 600000 | 1800000 | 最长空闲 30 分钟回收 |

建议：

```properties
timeBetweenEvictionRunsMillis=30000
minEvictableIdleTimeMillis=600000
maxEvictableIdleTimeMillis=1800000
```

这样可以：

- 减少频繁巡检开销
- 保留更久的热连接
- 通过 keepAlive 避免连接被网络设备静默断开

### 5.4 公平锁参数

| 参数 | 当前值 | 建议值 | 说明 |
|------|--------|--------|------|
| `useUnfairLock` | true | true | 高并发下吞吐更好 |

BI 场景下，连接池整体吞吐优先，保持 true 即可。

---

## 六、ClickHouse 建议配置

### 6.1 当前 URL

```text
jdbc:clickhouse://10.102.133.221:8123/?socketTimeout=300000&connectTimeout=300000
```

### 6.2 稳定优先建议 URL

ClickHouse 官方 Java/JDBC 文档示例中常见参数名为 `connect_timeout`、`socket_timeout`。不同驱动版本可能兼容驼峰写法，建议以当前驱动实际生效参数为准。

推荐：

```text
jdbc:clickhouse://10.102.133.221:8123/default
?connect_timeout=30000
&socket_timeout=300000
```

如果当前驱动确认使用驼峰参数：

```text
jdbc:clickhouse://10.102.133.221:8123/default
?connectTimeout=30000
&socketTimeout=300000
```

复杂查询或导出：

```text
jdbc:clickhouse://10.102.133.221:8123/default
?connect_timeout=30000
&socket_timeout=600000
```

### 6.3 ClickHouse 建议值

| 参数 | 建议值 |
|------|--------|
| `connectTimeout` | 30000 ms |
| `socketTimeout` | 300000 ms |
| 复杂查询 `socketTimeout` | 600000 ms |
| 导出 `socketTimeout` | 900000~1800000 ms |
| `maxActive` | 40~80 |
| `maxWait` | 30000 ms |

ClickHouse 查询可能扫描大量数据，建议：

- 保留较长 `socketTimeout`
- 慢查询不要挤占所有连接
- 大导出任务单独连接池
- 监控 `system.query_log`
- 对异常慢 SQL 做治理，而不是简单无限放大 timeout

---

## 七、StarRocks 建议配置

StarRocks 支持 MySQL 协议，常见连接方式：

```text
jdbc:mysql://<fe_host>:9030/<database>
```

或：

```text
jdbc:starrocks://<fe_host>:9030/default_catalog.<database>
```

### 7.1 稳定优先 URL

```text
jdbc:mysql://starrocks-fe:9030/db_name
?connectTimeout=30000
&socketTimeout=300000
&tcpKeepAlive=true
&useUnicode=true
&characterEncoding=utf8
&useSSL=false
&serverTimezone=Asia/Shanghai
```

复杂查询：

```text
jdbc:mysql://starrocks-fe:9030/db_name
?connectTimeout=30000
&socketTimeout=600000
&tcpKeepAlive=true
&useUnicode=true
&characterEncoding=utf8
&useSSL=false
&serverTimezone=Asia/Shanghai
```

### 7.2 StarRocks 建议值

| 参数 | 建议值 |
|------|--------|
| `connectTimeout` | 30000 ms |
| `socketTimeout` | 300000 ms |
| 复杂查询 `socketTimeout` | 600000 ms |
| `tcpKeepAlive` | true |
| `maxActive` | 40~60 |
| `maxWait` | 30000 ms |

StarRocks 是 MPP 架构，连接数过高会放大 FE/BE 压力。稳定优先不等于无限并发：

- 查询并发要受控
- 大查询单独连接池
- 关注 FE/BE CPU、内存、查询队列
- 对用户自助分析增加并发限制

---

## 八、MySQL 建议配置

MySQL 示例：

```text
jdbc:mysql://mysql-host:3306/db_name
?connectTimeout=30000
&socketTimeout=300000
&tcpKeepAlive=true
&useUnicode=true
&characterEncoding=utf8
&useSSL=false
&serverTimezone=Asia/Shanghai
```

### 8.1 MySQL 建议值

| 参数 | 建议值 |
|------|--------|
| `connectTimeout` | 10000~30000 ms |
| `socketTimeout` | 120000~300000 ms |
| `tcpKeepAlive` | true |
| `maxActive` | 20~40 |
| `maxWait` | 30000 ms |

MySQL 不适合承载大量复杂 BI 聚合查询。为了稳定：

- MySQL 主要用于维表、配置、轻量查询
- 大宽表分析应进入 ClickHouse / StarRocks
- 避免大量 BI 用户直接扫 MySQL 大表
- `maxActive` 不宜过大，否则会拖垮 MySQL

---

## 九、三类数据源建议值汇总

### 9.1 JDBC URL 参数

| 数据源 | 查询类型 | `connectTimeout` | `socketTimeout` |
|--------|----------|------------------|-----------------|
| ClickHouse | 看板 / 常规分析 | 30000 ms | 300000 ms |
| ClickHouse | 复杂分析 | 30000 ms | 600000 ms |
| ClickHouse | 导出 | 30000~60000 ms | 900000~1800000 ms |
| StarRocks | 看板 / 常规分析 | 30000 ms | 300000 ms |
| StarRocks | 复杂分析 | 30000 ms | 600000 ms |
| StarRocks | 导出 | 30000~60000 ms | 900000~1800000 ms |
| MySQL | 轻量查询 | 10000~30000 ms | 120000~300000 ms |
| MySQL | 复杂分析 | 不建议直接承载 | 不建议直接承载 |

### 9.2 标准 BI 稳定连接池

```properties
initialSize=20
minIdle=20
maxActive=40
maxWait=30000

validationQuery=select 1
testOnBorrow=true
testOnReturn=false
testWhileIdle=true
keepAlive=true

timeBetweenEvictionRunsMillis=30000
minEvictableIdleTimeMillis=600000
maxEvictableIdleTimeMillis=1800000

useUnfairLock=true
```

### 9.3 高并发 BI 稳定连接池

```properties
initialSize=20
minIdle=20
maxActive=60
maxWait=30000

validationQuery=select 1
testOnBorrow=true
testOnReturn=false
testWhileIdle=true
keepAlive=true

timeBetweenEvictionRunsMillis=30000
minEvictableIdleTimeMillis=600000
maxEvictableIdleTimeMillis=1800000

useUnfairLock=true
```

### 9.4 导出 / 复杂查询连接池

```properties
initialSize=5
minIdle=5
maxActive=10
maxWait=60000

validationQuery=select 1
testOnBorrow=true
testOnReturn=false
testWhileIdle=true
keepAlive=true

timeBetweenEvictionRunsMillis=30000
minEvictableIdleTimeMillis=600000
maxEvictableIdleTimeMillis=1800000

useUnfairLock=true
```

---

## 十、当前配置推荐调整

当前：

```properties
connectTimeout=300000
socketTimeout=300000
minIdle=20
initialSize=20
maxActive=40
maxWait=10000
testOnBorrow=false
testWhileIdle=true
keepAlive=true
timeBetweenEvictionRunsMillis=6000
minEvictableIdleTimeMillis=120000
maxEvictableIdleTimeMillis=600000
```

建议改为稳定优先版：

```properties
connectTimeout=30000
socketTimeout=300000

initialSize=20
minIdle=20
maxActive=40
maxWait=30000

validationQuery=select 1
testOnBorrow=true
testOnReturn=false
testWhileIdle=true
keepAlive=true

timeBetweenEvictionRunsMillis=30000
minEvictableIdleTimeMillis=600000
maxEvictableIdleTimeMillis=1800000

useUnfairLock=true
```

如果查询确实经常超过 5 分钟，不建议继续拉长主连接池，而是新增复杂查询池：

```properties
connectTimeout=30000
socketTimeout=600000
initialSize=5
minIdle=5
maxActive=10
maxWait=60000
testOnBorrow=true
testWhileIdle=true
keepAlive=true
```

---

## 十一、监控建议

稳定优先必须配套监控，否则长等待会掩盖问题。

| 指标 | 建议告警 |
|------|----------|
| 活跃连接数 | 持续超过 `maxActive * 80%` |
| 等待连接线程数 | 持续 > 0 超过 1 分钟 |
| 获取连接耗时 | P95 > 1 秒 |
| SQL 查询耗时 | P95 / P99 突增 |
| socket timeout 次数 | 任意突增 |
| connect timeout 次数 | 任意突增 |
| validationQuery 失败次数 | 连续失败告警 |
| 数据库慢查询数 | 超阈值告警 |
| 数据库连接数 | 接近数据库上限告警 |

---

## 十二、最终建议

针对 BI 系统，推荐采用以下默认策略：

```text
常规 BI 查询：
connectTimeout=30000
socketTimeout=300000
maxWait=30000
maxActive=40
testOnBorrow=true
keepAlive=true

复杂查询 / 导出：
connectTimeout=30000
socketTimeout=600000~1800000
maxWait=60000
maxActive=10
testOnBorrow=true
keepAlive=true
```

最终原则：

1. **不要快失败**：数据库轻微抖动时，应允许等待和恢复。
2. **也不要无限等**：连接建立不建议 5 分钟，30 秒更合理。
3. **优先保证连接有效**：`testOnBorrow=true` 更适合稳定优先。
4. **保留热连接**：`initialSize=20`、`minIdle=20` 对 BI 看板合理。
5. **复杂查询拆池**：不要让导出任务拖垮看板查询。
6. **必须监控**：长超时配置必须配合连接池和慢查询监控。

---

*最后更新：2026 年 5 月 14 日*
