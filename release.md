版本日志
===============
# v1.1.11

- add: raise http fail with detail

# v1.1.10

- bugfix: sql converter equals syntax error

# v1.1.9

- add: is_allowed_with_policy_cache for repeat calls of same subject-system-action policies

# v1.1.8

- add: do_migrate support feature_shield_rules

# v1.1.7

- add: do_migrate support common_actions

# v1.1.6

- bugfix: missing import os in do_migrate.py

# v1.1.5

- add: dummy_iam for mock and testing
- add: 添加属性新建关联函数

# v1.1.4

- bugfix: setup.py import version coding error while install

# v1.1.3

- bugfix: 修正 do_migrate 中 BK_IAM_HOST 的取值及默认值
- add: BKAPP_IAM_API_DEBUG/BKAPP_IAM_API_FORCE in environ for api debug
- add: search instance dispatcher
- add: another shortcut of tastypie

# v1.1.2

- bugfix: 修复通过 pip 安装方式使用时无法使用 iam_makemigrations 命令的问题

# v1.1.1

- bugfix: missing iam_migration/templates in dist package

# v1.1.0

- update: is_basic_auth_allowed log level to error if fail

# v1.0.9

- change: remove `six<1.15.0`, support `six>=1.11.0`

# v1.0.8

- bugfix: 生成无权限申请数据时支持根据 _bk_iam_path_ 生成父实例信息
- add: 增加batch_resource_creator_action接口
- add: 新增 资源批量授权/回收 ，policy list 拉取系统下某个操作的策略列表(翻页) api的支持

# v1.0.7

- bugfix: setup.py read __version__ fail

# v1.0.4

- update: six version >=1.11.0 and <=1.15.0
- change: 根据用户配置的API_PREFIX进行匹配返回对应的状态码
- add: is_allowed_with_cache for cache 10s for insensitive permission

# v1.0.3

- add: 授权回收接口grant_or_revoke_instance_permission/grant_or_revoke_path_permission

# v1.0.2

- add: do_migrate.py支持新建关联权限配置 upsert_resource_creator_actions
- add: iam 支持新建关联授权接口

# v1.0.0

- bugfix: 修复 IAM 调用 fetch_instance_info 接口失败的问题（需要更新 `iam.resource.provider.ResourceProvider` 子类中 `fetch_instance_info` 的签名为 `def fetch_instance_info(self, filter, **options)`）

# v0.0.12

- add: do_migrate support upsert_action_groups

# v0.0.11

- bugfix: 修复 page obj slice_from 和 slice_to 生成逻辑不正确的问题
- remove: read README.md for long_description in setup.py
- remove: iam_resource_owner from docs

# v0.0.10

- bugfix: python2/3 super syntax error
- breaking changes: muti_actions func response action key change from `["action_id"]` to `["action"]["id"]`

# v0.0.9

- bugfix

# v0.0.8

- 增加 resource 模块, 提供 ResourceAPI Provider 及 Dispatcher
- bugfix
- add curl in debug log
- add iam logger
- update do_migrate.py

# v0.0.7

- 使用 poetry 管理项目
- `make_filter` 支持传递外部 Converter

# v0.0.6

- 增加iam logger流水日志配置说明
- 优化iam logger info/error打印详情

# v0.0.5

- debug支持打印request_id
- debug支持打印curl, 方便自行调试
- debug模式下, 调用api会加入`?debug`, 返回结果中包含策略调试的上下文详细信息
- 支持Resource API Framework

# v0.0.4

- add: djaong migration支持
- contrib: tastypie
- add: 支持iam.meta配置元信息
- add: 支持批量资源鉴权
- add: 支持批量资源批量action是否有权限判断
- ops: 增加gitlab-ci, 支持lint / python2+python3 unittest
- fix: all lint issues
- unittest: 增加iam.IAM对象单元测试
- add: shortcut & exceptions

# v0.0.3

- 支持logging debug, 同时输出调用耗时
- 修复无权限返回空策略bug
- 增加转化为queryset的field字段映射转换
- 修复 ANY 表达式求值bug
- 增加支持打包
- 增加文档示例: 开启debug/鉴权/获取有权限的列表

# v0.0.2

- 支持表达式求值+表达式解析

# v0.0.1

- 基本代码框架+原型
- python版本的表达式求值的demo
