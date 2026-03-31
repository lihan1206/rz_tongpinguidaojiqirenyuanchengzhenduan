# 瞳骋轨道机器人远程诊断系统 - 重构架构文档

## 一、重构后的目录结构

```
refactored-java/
├── pom.xml                                    # Maven 构建配置
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/tongping/robot/
│   │   │       ├── RobotDiagnosisApplication.java    # 应用启动类
│   │   │       │
│   │   │       ├── controller/                # Controller 层 - 处理 HTTP 请求
│   │   │       │   ├── SensorController.java
│   │   │       │   ├── FaultRuleController.java
│   │   │       │   └── FaultLogController.java
│   │   │       │
│   │   │       ├── service/                   # Service 层 - 业务逻辑
│   │   │       │   ├── SensorDataService.java
│   │   │       │   ├── FaultRuleService.java
│   │   │       │   ├── FaultLogService.java
│   │   │       │   ├── impl/                  # 服务实现
│   │   │       │   │   ├── SensorDataServiceImpl.java
│   │   │       │   │   ├── FaultRuleServiceImpl.java
│   │   │       │   │   └── FaultLogServiceImpl.java
│   │   │       │   └── strategy/              # 策略模式 - 诊断算法
│   │   │       │       ├── DiagnosisStrategy.java
│   │   │       │       ├── DiagnosisStrategyFactory.java
│   │   │       │       ├── TemperatureDiagnosisStrategy.java
│   │   │       │       ├── VibrationDiagnosisStrategy.java
│   │   │       │       ├── PositionDiagnosisStrategy.java
│   │   │       │       └── GenericDiagnosisStrategy.java
│   │   │       │
│   │   │       ├── repository/                # Repository 层 - 数据访问
│   │   │       │   ├── SensorDataRepository.java
│   │   │       │   ├── FaultRuleRepository.java
│   │   │       │   ├── FaultLogRepository.java
│   │   │       │   └── AlarmNotificationRepository.java
│   │   │       │
│   │   │       ├── entity/                    # 实体类 - 数据库映射
│   │   │       │   ├── SensorData.java
│   │   │       │   ├── FaultRule.java
│   │   │       │   ├── FaultLog.java
│   │   │       │   └── AlarmNotification.java
│   │   │       │
│   │   │       ├── dto/                       # DTO 层 - 数据传输对象
│   │   │       │   ├── request/               # 请求 DTO
│   │   │       │   │   ├── SensorDataRequest.java
│   │   │       │   │   ├── FaultRuleCreateRequest.java
│   │   │       │   │   ├── FaultLogStatusUpdateRequest.java
│   │   │       │   │   └── SensorQueryRequest.java
│   │   │       │   └── response/              # 响应 DTO
│   │   │       │       ├── SensorDataResponse.java
│   │   │       │       ├── FaultRuleResponse.java
│   │   │       │       ├── FaultLogResponse.java
│   │   │       │       ├── DiagnosisResultResponse.java
│   │   │       │       └── ApiResponse.java
│   │   │       │
│   │   │       ├── exception/                 # 异常处理
│   │   │       │   ├── BusinessException.java
│   │   │       │   ├── ErrorCode.java
│   │   │       │   ├── ResourceNotFoundException.java
│   │   │       │   ├── ValidationException.java
│   │   │       │   ├── DiagnosisException.java
│   │   │       │   └── handler/
│   │   │       │       └── GlobalExceptionHandler.java
│   │   │       │
│   │   │       └── mapper/                    # 实体映射器
│   │   │           └── EntityMapper.java
│   │   │
│   │   └── resources/
│   │       └── application.yml                # 应用配置
│   │
│   └── test/                                  # 单元测试
│       ├── java/com/tongping/robot/
│       │   ├── service/
│       │   │   ├── impl/
│       │   │   │   └── FaultRuleServiceImplTest.java
│       │   │   └── strategy/
│       │   │       ├── TemperatureDiagnosisStrategyTest.java
│       │   │       └── DiagnosisStrategyFactoryTest.java
│       │   ├── controller/
│       │   │   └── SensorControllerTest.java
│       │   └── exception/
│       │       └── handler/
│       │           └── GlobalExceptionHandlerTest.java
│       └── resources/
│           └── application-test.yml
```

## 二、分层架构说明

### 1. Controller 层
- **职责**: 接收 HTTP 请求，参数校验，调用 Service，返回统一响应
- **特点**:
  - 使用 `@Valid` 进行请求参数校验
  - 使用 `@Validated` 支持分组校验和方法级校验
  - 统一返回 `ApiResponse` 包装响应

### 2. Service 层
- **职责**: 业务逻辑处理，事务管理
- **特点**:
  - 接口与实现分离，便于测试和扩展
  - 使用 `@Transactional` 管理事务
  - 通过策略模式实现诊断算法的可扩展

### 3. Repository 层
- **职责**: 数据访问，数据库操作
- **特点**:
  - 继承 `JpaRepository`，获得基础 CRUD 能力
  - 使用方法命名约定定义查询
  - 使用 `@Query` 注解自定义复杂查询

### 4. DTO 层
- **职责**: 数据传输，解耦实体与接口
- **特点**:
  - 请求 DTO 使用 Bean Validation 注解校验
  - 响应 DTO 控制返回字段，避免暴露敏感信息
  - 使用 MapStruct 自动转换实体与 DTO

### 5. Entity 层
- **职责**: 数据库实体映射
- **特点**:
  - 使用 JPA 注解定义表结构
  - 与业务逻辑解耦，仅用于数据持久化

## 三、设计模式应用

### 1. 策略模式 (Strategy Pattern)

**应用场景**: 不同类型的传感器需要不同的诊断逻辑

**实现**:
```java
// 策略接口
public interface DiagnosisStrategy {
    String getSensorType();
    List<FaultRule> diagnose(Long robotId, BigDecimal value, List<FaultRule> rules);
}

// 具体策略
@Component
public class TemperatureDiagnosisStrategy implements DiagnosisStrategy {
    @Override
    public String getSensorType() { return "temperature"; }
    // 温度特定的诊断逻辑
}

@Component
public class VibrationDiagnosisStrategy implements DiagnosisStrategy {
    @Override
    public String getSensorType() { return "vibration"; }
    // 振动特定的诊断逻辑
}
```

**优势**:
- 新增传感器类型时，只需添加新的策略类，无需修改现有代码（开闭原则）
- 诊断逻辑分散到各个策略类，职责单一
- 便于单元测试，每个策略可独立测试

### 2. 工厂模式 (Factory Pattern)

**应用场景**: 根据传感器类型获取对应的诊断策略

**实现**:
```java
@Component
public class DiagnosisStrategyFactory {
    private final Map<String, DiagnosisStrategy> strategyMap = new HashMap<>();
    
    public DiagnosisStrategy getStrategy(String sensorType) {
        return strategyMap.getOrDefault(sensorType.toLowerCase(), genericStrategy);
    }
    
    public void registerStrategy(String sensorType, DiagnosisStrategy strategy) {
        strategyMap.put(sensorType.toLowerCase(), strategy);
    }
}
```

**优势**:
- 隐藏策略创建逻辑
- 支持运行时动态注册新策略
- 客户端无需关心具体策略类

### 3. 模板方法模式 (Template Method Pattern)

**应用场景**: 诊断策略的通用比较逻辑

**实现**:
```java
public interface DiagnosisStrategy {
    // 模板方法 - 通用比较逻辑
    default boolean isTriggered(String operator, BigDecimal value, BigDecimal threshold) {
        return switch (operator) {
            case ">" -> value.compareTo(threshold) > 0;
            case ">=" -> value.compareTo(threshold) >= 0;
            // ...
        };
    }
}
```

## 四、异常处理体系

### 1. 自定义异常层次

```
BusinessException (业务异常基类)
├── ResourceNotFoundException (资源不存在)
├── ValidationException (参数校验失败)
└── DiagnosisException (诊断异常)
```

### 2. 统一异常处理

使用 `@ControllerAdvice` 集中处理异常:

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException ex) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(ex.getCode(), ex.getMessage()));
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidationException(...) {
        // 处理 @Valid 校验失败
    }
}
```

### 3. 错误码规范

| 错误码范围 | 类型 |
|-----------|------|
| 1000-1999 | 系统级错误 |
| 2000-2999 | 参数错误 |
| 3000-3999 | 资源错误 |
| 4000-4999 | 业务错误 |
| 5000-5999 | 权限错误 |

## 五、扩展性设计

### 1. 新增传感器类型

以新增"湿度传感器"为例：

1. 创建新的策略类:
```java
@Component
public class HumidityDiagnosisStrategy implements DiagnosisStrategy {
    @Override
    public String getSensorType() {
        return "humidity";
    }
    
    @Override
    public List<FaultRule> diagnose(Long robotId, BigDecimal value, List<FaultRule> rules) {
        // 湿度特定的诊断逻辑
    }
}
```

2. 无需修改任何现有代码，Spring 会自动注入新策略

### 2. 新增诊断规则操作符

1. 在 `DiagnosisStrategy.isTriggered()` 方法中添加新 case
2. 更新 `FaultRuleCreateRequest` 中的校验注解

### 3. 新增告警通知渠道

1. 创建通知策略接口
2. 实现邮件、短信等具体通知策略
3. 在 `SensorDataServiceImpl` 中调用通知服务

## 六、技术选型说明

| 技术 | 版本 | 用途 |
|------|------|------|
| Spring Boot | 3.2.0 | 应用框架 |
| Spring Data JPA | 3.2.0 | 数据访问 |
| Spring Validation | 3.2.0 | 参数校验 |
| PostgreSQL | 14+ | 生产数据库 |
| H2 | 2.x | 测试数据库 |
| MapStruct | 1.5.5 | 实体映射 |
| Lombok | 1.18.30 | 代码简化 |
| SpringDoc | 2.3.0 | API 文档 |
| JUnit 5 | 5.10 | 单元测试 |
| Mockito | 5.x | 测试模拟 |

### 选型理由

1. **Spring Boot 3.x**: 基于 Java 17，性能更好，支持虚拟线程
2. **JPA + PostgreSQL**: 成熟稳定，支持复杂查询和事务
3. **MapStruct**: 编译期生成映射代码，性能优于反射方案
4. **SpringDoc**: 自动生成 OpenAPI 文档，支持 Swagger UI
5. **JUnit 5 + Mockito**: 现代测试框架，支持参数化测试和扩展

## 七、API 接口示例

### 接收传感器数据
```http
POST /api/v1/sensors/ingest
Content-Type: application/json

{
    "robotId": 1,
    "sensorType": "temperature",
    "value": 85.5
}

Response:
{
    "code": 200,
    "message": "数据接收成功",
    "data": {
        "robotId": 1,
        "sensorType": "temperature",
        "value": 85.5,
        "hasFault": true,
        "triggeredRules": [...],
        "faultLogs": [...]
    }
}
```

### 创建故障规则
```http
POST /api/v1/faults/rules
Content-Type: application/json

{
    "name": "温度过高告警",
    "sensorType": "temperature",
    "operator": ">",
    "threshold": 80.0,
    "level": "严重"
}
```

## 八、测试策略

1. **单元测试**: 使用 JUnit 5 + Mockito，覆盖 Service 和 Controller
2. **集成测试**: 使用 `@SpringBootTest` 和 H2 内存数据库
3. **参数化测试**: 使用 `@ParameterizedTest` 测试边界条件
4. **Web 测试**: 使用 `@WebMvcTest` 测试 Controller 层
