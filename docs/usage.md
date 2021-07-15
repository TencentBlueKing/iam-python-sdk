[toc]

## 1. 基本使用

### 1.1 开启debug 及配置流水日志


#### Debug

**注意**: `debug`仅在调试阶段开启, 生产环境请关闭(`iam_looger.setLevel(logging.ERROR)`);

生产环境开启带来问题:

1. 日志量过大
2. 影响请求速度(性能大幅降低)
3. 敏感信息泄漏(权限相关)

```python
from iam import IAM, Request, Subject, Action, Resource

import sys
import logging
iam_logger = logging.getLogger("iam")
iam_logger.setLevel(logging.DEBUG)

debug_hanler = logging.StreamHandler(sys.stdout)
debug_hanler.setFormatter(logging.Formatter('%(levelname)s [%(asctime)s] [IAM] %(message)s'))
iam_logger.addHandler(debug_hanler)
```

在调用sdk进行鉴权时, 会在终端打印debug日志

```
DEBUG [2020-05-21 14:23:22,833] [IAM] calling IAM.is_allowed(request)......
DEBUG [2020-05-21 14:23:22,833] [IAM] the request: {'action': {'id': 'access_developer_center'}, 'environment': {}, 'system': 'bk_paas', 'resources': [], 'subject': {'type': 'user', 'id': u'admin'}}
INFO [2020-05-21 14:23:22,918] [IAM] request: [method=`POST`, url=`http://{IAM_HOST}:8080/api/v1/policy/query`, data=`{'action': {'id': 'access_developer_center'}, 'environment': {}, 'system': 'bk_paas', 'resources': [], 'subject': {'type': 'user', 'id': u'admin'}}`]response: [status_code=`200`, request_id=`8e0c2a6f599248ecaad7579488956927`, content=`{"code":0,"message":"ok","data":{"field":"","op":"any","value":[]},"debug":{"time":"2020-05-21T14:23`]
DEBUG [2020-05-21 14:23:22,919] [IAM] the request id: `8e0c2a6f599248ecaad7579488956927`
DEBUG [2020-05-21 14:23:22,919] [IAM] the curl: `curl -X POST -H 'X-BK-APP-CODE: {APP_CODE}' -H 'X-BK-APP-SECRET: {APP_SECRET}' -H 'X-Bk-IAM-Version: 1' -d '{"action": {"id": "access_developer_center"}, "environment": {}, "system": "bk_paas", "resources": [], "subject": {"type": "user", "id": "admin"}}' 'http://127.0.0.1:8080/api/v1/policy/query?debug=true'`
DEBUG [2020-05-21 14:23:22,919] [IAM] do http request: method=`http_post`, url=`http://{IAM_HOST}/api/v1/policy/query`, data=`{"action": {"id": "access_developer_center"}, "environment": {}, "system": "bk_paas", "resources": [], "subject": {"type": "user", "id": "admin"}}`
DEBUG [2020-05-21 14:23:22,920] [IAM] http request result: ok=`True`, _data=`{"message": "ok", "code": 0, "data": {"field": "", "value": [], "op": "any"}}`
DEBUG [2020-05-21 14:23:22,920] [IAM] http request took 86 ms
DEBUG [2020-05-21 14:23:22,920] [IAM] the return policies: {u'field': u'', u'value': [], u'op': u'any'}
DEBUG [2020-05-21 14:23:22,920] [IAM] the return expr: ( any [])
DEBUG [2020-05-21 14:23:22,921] [IAM] the return expr render: (None any [])
DEBUG [2020-05-21 14:23:22,921] [IAM] the return expr eval: True
DEBUG [2020-05-21 14:23:22,921] [IAM] the return expr eval took 0 ms
```

其中:

- `request_id` 可以在问题排查时, 用于发给IAM服务端获取相关服务端处理日志
- `the curl` 可以直接复制, 用于复现执行, 注意`这里暴露了系统的访问鉴权信息`(**所以生产环境禁止开启debug**, 仅供开发联调使用)
- `http request took` 是单个请求的耗时, 可以用于确认`慢`的问题
- `the return expr` 包含最终表达式的原始数据/渲染数据/求值结果/求值耗时


#### API DEBUG

注意: `仅用于开发/联调环境排查定位问题, 一定不要在生产环境中开启, 将会导致API性能急剧下降`

可以设置环境变量:

- `IAM_API_DEBUG=true` or `BKAPP_IAM_API_DEBUG=true`: 会在api url中加入`?debug=true`, 使得请求返回json中多返回`debug`字段, 包含策略相关的完整上下文信息, 用于精确定位api执行过程
- `IAM_API_FORCE=true` or `BKAPP_IAM_API_FORCE=true`: 会在api url中加入`?force=true`, 请求将不走缓存, 直接从db中获取数据, 用于排查缓存类bug


#### 流水日志

生产环境, 可能需要保留IAM流水日志, 用于后续问题排查及定位

此时, 可以将`iam logger`配置到对应框架的日志配置中

注意:
- 日志级别设置为INFO: 请求流水日志, 包含成功/失败等(建议)
- 日志级别设置为ERROR: 报错日志, 网络请求及非200返回

以django为例

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        ......
    },
    'handlers': {
        ......
        # 增加iam heandler, 落地日志到日志目录, 文件名 xxx_iam.log, 并且按固定大小rotate, 保留固定个数
        'iam': {
            'class': LOG_CLASS,
            'formatter': 'verbose',
            'filename': os.path.join(LOGGING_DIR, 'xxx_iam.log'),
            'maxBytes': LOG_MAX_BYTES,
            'backupCount': LOG_BACKUP_COUNT
        },
    },
    'loggers': {
        ......
        # 配置iam logger, 使用iam handler, 日志级别同项目配置的LOGGER_LEVEL
        'iam': {
            'handlers': ['iam'],
            'level': LOGGER_LEVEL,
            'propagate': True,
        },
    }
}
```



### 1.2 is_allowed

**注意**, 对于非敏感权限, 可以调用`is_allowed_with_cache(request)`, 默认缓存10s.
(注意: 不要用于新建关联权限的资源is_allowed判定, 否则可能新建一个资源新建关联生效之后跳转依旧没权限; 更多用于`管理权限/未依赖资源的权限`权限判断)

```python
    # cache 10s, 10s不会重新请求权限并进行鉴权计算, 能加快前端的体验
    self._iam.is_allowed_with_cache(request)
```


> 查询是否有某个操作权限(没有资源实例), 例如访问开发者中心

```python
from iam import IAM, Request, Subject, Action, Resource

class Permission(object):
    def __init__(self):
        self._iam = IAM(APP_CODE, APP_SECRET, BK_IAM_HOST, BK_PAAS_HOST)

    def _make_request_without_resources(self, username, action_id):
        request = Request(
            SYSTEM_ID,
            Subject("user", username),
            Action(action_id),
            None,
            None,
        )
        return request

    def allowed_access_developer_center(self, username):
        """
        访问开发者中心权限
        """
        request = self._make_request_without_resources(username, "access_developer_center")
        return self._iam.is_allowed(request)
```

> 查询是否有某个资源的某个操作权限(有资源实例), 例如管理某个应用

```python
class Permission(object):
    def __init__(self):
        self._iam = IAM(APP_CODE, APP_SECRET, BK_IAM_HOST, BK_PAAS_HOST)

    def _make_request_with_resources(self, username, action_id, resources):
        request = Request(
            SYSTEM_ID,
            Subject("user", username),
            Action(action_id),
            resources,
            None,
        )
        return request

    def allowed_develop_app(self, username, app_code):
        """
        app开发权限
        """
        r = Resource(SYSTEM_ID, 'app', app_code, {})
        resources = [r]
        request = self._make_request_with_resources(username, "develop_app", resources)
        return self._iam.is_allowed(request)
```


如果需要对一批资源同时进行鉴权, 可以调用`batch_is_allowed` (注意这个封装不支持跨系统资源依赖, 只支持接入系统自己的本地资源

```python

subject = Subject("user", "tom")
action = Action("flow_edit")

resource1 = Resource("bk_sops", "flow", "1", {})
resource2 = Resource("bk_sops", "flow", "2", {})
resource3 = Resource("bk_sops", "flow", "3", {})

# 注意这里resources字段空
request = Request(
    "bk_sops",
    subject,
    action,
    [],
    None
)


iam = IAM("bk_sops", "app_secret", "bk_iam_host", "bk_paas_host")

iam.batch_is_allowed(request, [[resource1], [resource2], [resource3]]))
# {'1': True, '2': False, '3': True}
```

### 1.3 make_filter

> 查询某个用户有权限的资源列表, 例如查询某个用户有开发权限的应用列表

```python
    def app_list(self, username):
        """
        用户有权限的应用列表

        拉回策略, 自己算!
        """
        request = self._make_request_without_resources(username, "develop_app")

        # 注册的资源类型是app, 所以返回策略中是app.id eq xxx;
        # 但是数据库中queryset过滤的字段名是code, 所以需要做个转换;
        # 数据库中将父级资源的 id 记录再了 parent_id 字段上，也需要定义转换
        key_mapping = {"app.id": "code", "app.path": "parent_id"}


        # 需要会将权限中心保存的 /resource_type,id/ path 转换为数据库中存储的 id 形式
        def path_value_hook(value):
            # get id in "/project,id/"
            return value[1:-1].split(",")[1]
        value_hooks = {"app.path": path_value_hook}

        # 默认make_filter使用的是DjangoQuerySetConverter
        filters = self._iam.make_filter(request, key_mapping=key_mapping, value_hooks=value_hooks)
        # 如果从服务端查不到策略, 代表没有任何权限
        if not filters:
            return []

        # 直接用django queryset查
        apps = App.objects.filter(filters).all()
        print("apps", apps)
        return [app.code for app in apps]
```

### 1.4 获取无权限申请跳转url

> 没有权限时, 在前端展示要申请的权限列表, 需要访问IAM接口, 拿到申请权限url; 用户点击跳转到IAM SaaS对应页面申请权限

文档: TODO

- 申请不带资源实例的权限

```python
from iam.apply.models import ActionWithoutResources, ActionWithResources, Application, RelatedResourceType
from iam.apply.models import ResourceInstance, ResourceNode

class Permission(object):
    def __init__(self):
        self._iam = IAM(APP_CODE, APP_SECRET, BK_IAM_HOST, BK_PAAS_HOST)

    def make_no_resource_application(self, action_id):
        # 1. make application
        action = ActionWithoutResources(action_id)
        actions = [action]

        application = Application(SYSTEM_ID, actions)
        return application

    def generate_apply_url(self, bk_token, application):
        """
        处理无权限 - 跳转申请列表
        """
        # 2. get url
        ok, message, url = self._iam.get_apply_url(application, bk_token)
        if not ok:
            logger.error("iam generate apply url fail: %s", message)
            return IAM_APP_URL
        return url
```

- 申请带资源实例的权限

```python
from iam.apply.models import ActionWithoutResources, ActionWithResources, Application, RelatedResourceType
from iam.apply.models import ResourceInstance, ResourceNode


class Permission(object):
    def __init__(self):
        self._iam = IAM(APP_CODE, APP_SECRET, BK_IAM_HOST, BK_PAAS_HOST)

    def make_resource_application(self, action_id, resource_type, resource_id, resource_name):
        # 1. make application
        # 这里支持带层级的资源, 例如 biz: 1/set: 2/host: 3
        # 如果不带层级, list中只有对应资源实例
        instance = ResourceInstance([ResourceNode(resource_type, resource_id, resource_name)])
        # 同一个资源类型可以包含多个资源
        related_resource_type = RelatedResourceType(SYSTEM_ID, resource_type, [instance])
        action = ActionWithResources(action_id, [related_resource_type])

        actions = [action, ]
        application = Application(SYSTEM_ID, actions)
        return application

    def generate_apply_url(self, bk_token, application):
        """
        处理无权限 - 跳转申请列表
        """
        # 2. get url
        ok, message, url = self._iam.get_apply_url(application, bk_token)
        if not ok:
            logger.error("iam generate apply url fail: %s", message)
            return IAM_APP_URL
        return url
```


### 1.5 获取用户关于某批资源某批操作的权限信息

> 进入资源列表也，可能需要在前端展示当前用户关于列表中的资源的一批操作的权限信息

```python
subject = Subject("user", "tom")
action1 = Action("flow_edit")
action2 = Action("flow_view")
action3 = Action("flow_delete")
resource1 = Resource("bk_sops", "flow", "1", {})
resource2 = Resource("bk_sops", "flow", "2", {})
resource3 = Resource("bk_sops", "flow", "3", {})

request = MultiActionRequest(
    "bk_sops",
    subject,
    [action1, action2, action3],
    [],
    None
)


iam = IAM(
    "bk_sops", "app_secret",
    "bk_iam_host", "bk_paas_host"
)
iam.batch_resource_multi_actions_allowed(request, [[resource1], [resource2], [resource3]]))
# {'1': {'flow_edit': True, 'flow_view': True, 'flow_delete': False}, '2': {'flow_edit': True, 'flow_view': True, 'flow_delete': False}, '3': {'flow_edit': True, 'flow_view': True, 'flow_delete': False}}
```

或者, 获取一个资源某批操作的权限信息


```python
subject = Subject("user", "tom")
action1 = Action("flow_edit")
action2 = Action("flow_view")
action3 = Action("flow_delete")
resource1 = Resource("bk_sops", "flow", "1", {})

request = MultiActionRequest(
    "bk_sops",
    subject,
    [action1, action2, action3],
    [resource1],
    None
)


iam = IAM(
    "bk_sops", "app_secret",
    "bk_iam_host", "bk_paas_host"
)
iam.resource_multi_actions_allowed(request)
# {'flow_edit': True, 'flow_view': True, 'flow_delete': False}
```



### 1.6 生成无权限描述协议数据

使用 `iam.utils.gen_perms_apply_data` 可以生成生成[无权限描述协议数据](#)，其接收参数如下：

- `system`：系统 ID
- `subject`：`Subject` 对象
- `action_to_resources_list`：无权动作与相关资源实例的映射列表，格式为：
    ```
    [
        {
            "action": Action,
            "resources_list": [[resource1, resource2], [resource1, resource2]]
        },
        ...
    ]
    ```
    单个 action 中对应的 resources_list 必须是同类型的 Resource

使用示例：

```python
from iam.utils import gen_perms_apply_data

system = "test_system"
subject = Subject("user", "admin")

action1 = Action("action1")
action2 = Action("action2")
action3 = Action("action3")

resource1 = Resource("test_system", "r1", "r1id", {"name": "r1n"})
resource2 = Resource("test_system", "r2", "r2id", None)
resource3 = Resource("test_system", "r3", "r3id", {})
resource4 = Resource("another_system", "r4", "r4id", {"name": "r4n"})
resource5 = Resource("another_system", "r4", "r5id", {"name": "r5n"})

data = gen_perms_apply_data(
    system,
    subject,
    [
        {"action": action1, "resources_list": [[resource1, resource2, resource3, resource4]]},  # 含有拓扑层级的资源
        {"action": action2, "resources_list": [[]]},  # 不关联资源类型的操作
        {
            "action": action3,  # 带有跨系统依赖的资源
            "resources_list": [
                [resource1, resource3, resource4],
            ],
        },
    ],
)
```

### 1.7 通过API请求返回无权限的通用配置

 sdk提供`AuthFailedExceptionMiddleware` 特殊处理鉴权不通过异常`AuthFailedBaseException`的时候，默认返回HTTP状态码为`499`，API的请求则可以通过在`settings`中配置参数`BK_IAM_API_PREFIX`进行前缀匹配，匹配通过时返回的状态码为`200`

 使用示例：

 ```python
 # settings.py 配置如下：

BK_IAM_API_PREFIX = SITE_URL + 'openapi'

```



------------------------------

## 2. IAM Migration

### 2.1 Django Migration

1. 将 `iam.contrib.iam_migration` 加入 `INSTALLED_APPS` 中
2. 在项目根目录的 `support-files/iam/` 中添加 iam migration json 文件
3. 执行 `python manage.py iam_makemigrations {migration_json_file_name}` （其中 `migration_json_file_name}` 为新加入的 iam migration json 文件名），该命令会在 `iam/contrib/iam_migration/migrations` 目录下生成用于执行向权限中心注册系统、资源和操作的 migration 文件，当应用第一次部署时，这些 migration 文件会随之执行。
    - **注意：如果你的 iam sdk 不是以源码的方式嵌入项目中而是以 pip 的方式安装的，那么请额外配置 `BK_IAM_MIGRATION_APP_NAME` 来设置用于存储 migration 文件的 APP**

#### 2.2 CONFIG

- `APP_CODE/SECRET_KEY` 应用在蓝鲸开发者中心申请应用的`app_code/app_secret`
- `BK_IAM_SYSTEM_ID` 接入系统注册到权限中心使用的系统 ID(system_id)
- `BK_IAM_INNER_HOST` 权限中心后台的地址
- `BK_IAM_MIGRATION_JSON_PATH`：如果你不想将 iam migration json 放置在 `support-files/iam/` 目录下，请在 Django Setting 中将该变量配置为你想要存放 iam migration json 文件的相对目录
- `BK_IAM_RESOURCE_API_HOST`：如果你无法确定 upsert_system 操作 data 中的 `provider_config.host` 的值，那么可以在 Django Setting 中配置这个变量，IAM Migration 会在执行 upsert_system 操作前将 `provider_config.host` 设置为 `BK_IAM_RESOURCE_API_HOST`
- `BK_IAM_MIGRATION_APP_NAME`：如果你是以 pip 的方式安装 iam sdk，那么请单独新建一个 Django app，将 `BK_IAM_MIGRATION_APP_NAME` 设置为该 app 的 label，并将该 app 加入 `INSTALLED_APPS` 中，iam migrator 会将 Django migration 文件置于该 app 的 `migrations` 目录下。
- `BK_IAM_SKIP`: 是否跳过iam migration, 某些版本sdk强依赖, 可以设置成`False`或`None`
  - >TIPS：
    > - 可以使用 `python manage.py startapp {app_name}` 命令来新建 django app
    > - 如果 app 是已存在的，请确保该 app 目录下存在 `migrations/__init__.py` 文件）

------------------------------

## 3. Resource API Framework

SDK 提供了 Resource API Framework，它能够帮助你处理 Resource API 必须处理的一些公共逻辑（鉴权，参数校验，响应标准化等），还提供了提供不同 Web 框架（Django）API 的 Dispatcher。

Resource API Framework 中有两个核心概念：

- **ResourceProvider**：封装不同类型的资源在处理来自 IAM 不同类型的方法时的处理逻辑
- **Dispatcher**：针对不同的 Web 框架，提供 API 的定义

### 3.1 ResourceProvider 的定义

用户自定义的 Provider 必须继承自 `iam.resource.provider.ResourceProvider`，并且实现以下方法：

- `list_attr(**options)`：处理来自 IAM 的 list_attr 请求
  - 输入：
    - `options`：
      - `language(str)`：国际化语言
  - 输出：返回 `iam.resource.provider.ListResult` 的实例，其中 `results` 应满足 IAM list_attr 响应协议
- `list_attr_value(filter, page, **options)`：处理来自 IAM 的 list_attr_value 请求
  - 输入：
    - `filter`：过滤器对象
      - `filter.attr(str)`：需要查询的资源属性id
      - `filter.keyword(str)`：资源属性值的搜索关键字
      - `filter.ids(list[string,int,bool])`：资源属性值ID列表
    - `page`：分页对象
      - `page.limit(int)`：查询数量
      - `page.offset(int)`：查询偏移
    - `options`：
      - `language(str)`：国际化语言
  - 输出：返回 `iam.resource.provider.ListResult` 的实例，其中 `results` 应满足 IAM list_attr_value 响应协议
- `list_instance(filter, page, **options)`：处理来自 IAM 的 list_instance 请求
  - 输入：
    - `filter`：过滤器对象
      - `filter.parent(dict)`：资源的直接上级，具体包含type和id，type为直接上级资源的类型，id为直接上级资源实例ID
      - `filter.search(str)`：资源实例的搜索关键字
      - `filter.resource_type_chain(list[dict])`：配置search参数一起使用，resource_type_chain指定返回对象返回的祖先层级拓扑
    - `page`：分页对象
      - `page.limit(int)`：查询数量
      - `page.offset(int)`：查询偏移
    - `options`：
      - `language`：国际化语言
  - 输出：返回 `iam.resource.provider.ListResult` 的实例，其中 `results` 应满足 IAM list_instance 响应协议
- `fetch_instance_info(filter, page, **options)`：处理来自 IAM 的 fetch_instance_info 请求
  - 输入：
    - `filter`：过滤器对象
      - `filter.ids(list[str])`：需要查询的资源实例的唯一标识列表
      - `filter.attrs(lsit[str])`：需要查询的资源属性列表，比如["path", "os"]，空列表或无该参数则表示查询所有属性
    - `options`：
      - `language`：国际化语言
  - 输出：返回 `iam.resource.provider.ListResult` 的实例，其中 `results` 应满足 IAM fetch_instance_info 响应协议
- `list_instance_by_policy(filter, page, **options)`：处理来自 IAM 的 list_instance_by_policy 请求
  - 输入：
    - `filter`：过滤器对象
      - `filter.expression(dict)`：资源的表达式，[协议请查看](#)
    - `page`：分页对象
      - `page.limit(int)`：查询数量
      - `page.offset(int)`：查询偏移
    - `options`：
      - `language`：国际化语言
  - 输出：返回 `iam.resource.provider.ListResult` 的实例，其中 `results` 应满足 IAM list_instance_by_policy 响应协议

除此之外，如果 Provider 中定义了 `pre_{method}` 方法（`method` 可选值（`list_attr`, `list_attr_value`, `list_instance`, `fetch_instance_info`, `list_instance_by_policy`），Dispatcher 会在调用对应的 `{method}` 方法前调用其对应的 `pre` 方法进行预处理，下面的例子检测 `list_instance` 中传入的 page 对象，如果 limit 过大，则拒绝该请求：

```python
class TaskResourceProvider(ResourceProvider):
    def pre_list_instance(self, filter, page, **options):
        if page.limit == 0 or page.limit > 50:
            raise InvalidPageException("limit in page too large")
    ...
```

下面是一种资源类型的 Provider 定义示例：

```python
from iam.resource.provider import ResourceProvider, ListResult

class ProjectResourceProvider(ResourceProvider):
    def list_attr(self, **options):
        results = get_project_list_attr()
        return ListResult(results=results)

    def list_attr_value(self, filter, page, **options):
        results = get_project_list_attr_value()
        return ListResult(results=results)

    def list_instance(self, filter, page, **options):
        results = get_project_instance()
        return ListResult(results=results)

    def fetch_instance_info(self, filter, **options):
        results = get_project_instance_detail()
        return ListResult(results=results)

    def list_instance_by_policy(self, filter, page, **options):
        results = get_project_instance_by_policy()
        return ListResult(results=results)
```

### 3.2 Dispatcher

#### 3.2.1 Django Dispatcher

`iam.contrib.django.dispatcher.DjangoBasicResourceApiDispatcher` 是适用于 Django 的 Resource API Dispatcher

##### `__init__`

- `iam`：对应系统的 `iam.IAM` 实例
- `system`：对应系统的 ID (**注意**, `这里是systemID, 不是app_code, 一定不能传app_code, 某些环境systemID不一定是app_code`)


#### `register(resource_type, provieprovider)`

注册类型为 `resource_type` 的 Provider

- `resource_type`：资源类型
- `provider`：`iam.resource.provider.ResourceProvider` 的子类实例


#### `as_view(decorators=[])`

返回能够作为 Resource API 的 view 函数

- `decorators`：需要装饰返回 view 函数的装饰器列表

#### 3.2.2 使用示例：

```python
from blueapps.account.decorators import login_exempt
from iam import IAM
from iam.contrib.django.dispatcher import DjangoBasicResourceApiDispatcher
from iam.resource.provider import ResourceProvider, ListResult
from django.conf.urls import url, include

iam = IAM(
    "my_system", "app_secret",
    "iam_api_host", "paas_host"
)

def flow_path_value_hook(value):
    # get id in "/project,id/"
    return value[1:-1].split(",")[1]


class FlowResourceProvider(ResourceProvider):
    def list_attr(self, **options):
        """
        flow 资源没有属性，返回空
        """
        return ListResult(results=[])

    def list_attr_value(self, filter, page, **options):
        """
        flow 资源没有属性，返回空
        """
        return ListResult(results=[])

    def list_instance(self, filter, page, **options):
        """
        flow 上层资源为 project
        """
        queryset = []
        with_path = False

        if not (filter.parent or filter.search or filter.resource_type_chain):
            queryset = TaskTemplate.objects.all()
        elif filter.parent:
            parent_id = filter.parent["id"]
            if parent_id:
                queryset = TaskTemplate.objects.filter(project_id=str(parent_id))
        elif filter.search and filter.resource_type_chain:
            # 返回结果需要带上资源拓扑路径信息
            with_path = True
            # 过滤 project flow 名称
            project_keywords = filter.search.get("project", [])
            flow_keywords = filter.search.get("flow", [])

            project_filter = Q()
            flow_filter = Q()

            for keyword in project_keywords:
                project_filter |= Q(name__icontains=keyword)

            for keyword in flow_keywords:
                flow_filter |= Q(pipeline_template__name__icontains=keyword)

            project_ids = Project.objects.filter(project_filter).values_list("id", flat=True)
            queryset = TaskTemplate.objects.filter(project_id__in=list(project_ids)).filter(flow_filter)

        results = [
            {"id": str(flow.id), "display_name": flow.name} for flow in queryset[page.slice_from : page.slice_to]
        ]

        if with_path:
            results = [
                {
                    "id": str(flow.id),
                    "display_name": flow.name,
                    "path": [[{"type": "project", "id": str(flow.project_id), "display_name": flow.project.name}]],
                }
                for flow in queryset[page.slice_from : page.slice_to]
            ]

        return ListResult(results=results)

    def fetch_instance_info(self, filter, **options):
        """
        flow 没有定义属性，只处理 filter 中的 ids 字段
        """
        ids = []
        if filter.ids:
            ids = [int(i) for i in filter.ids]

        results = [{"id": str(flow.id), "display_name": flow.name} for flow in TaskTemplate.objects.filter(id__in=ids)]
        return ListResult(results=results)

    def list_instance_by_policy(self, filter, page, **options):
        """
        flow
        """

        expression = filter.expression
        if not expression:
            return ListResult(results=[])

        key_mapping = {
            "flow.id": "id",
            "flow.owner": "pipeline_template__creator",
            "flow.path": "project__id",
        }
        # 这里使用 PathEqDjangoQuerySetConverter 是为了将对 flow.path 的 starts_with 操作符转换为 eq 操作符
        converter = PathEqDjangoQuerySetConverter(key_mapping, {"flow.path": flow_path_value_hook})
        filters = converter.convert(expression)

        results = [
            {"id": str(flow.id), "display_name": flow.name}
            for flow in TaskTemplate.objects.filter(filters)[page.slice_from : page.slice_to]
        ]

        return ListResult(results=results)


dispatcher = DjangoBasicResourceApiDispatcher(iam, "my_system")
dispatcher.register("flow", FlowResourceProvider())


urlpatterns = [
    url(r'^resource/api/v1/$', dispatcher.as_view([login_exempt]))
]
```
