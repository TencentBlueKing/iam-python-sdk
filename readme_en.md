[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](https://github.com/TencentBlueKing/iam-python-sdk/blob/master/LICENSE.txt) [![Release Version](https://img.shields.io/badge/release-1.1.9-brightgreen.svg)](https://github.com/TencentBlueKing/iam-python-sdk/releases) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/TencentBlueKing/iam-python-sdk/pulls)

[(English Documents Available)](readme_en.md)

## Overview

iam-python-sdk is the SDK of blueking IAM(BK-IAM), your system can use BK-IAM easily via SDK.

## Features

- [Basic] 兼容Python2/Python3
- [Basic] 完备的单元测试
- [Basic] 支持debug调试完整流程
- [IAM] 支持条件表达式求值: 策略查询/鉴权/获取有权限的用户列表
- [IAM] 支持条件表达式解析: 转换成Django QuerySet及SQL语句
- [IAM] 获取无权限申请跳转URL
- [IAM] 支持批量资源鉴权 / 支持批量资源批量action是否有权限判断
- [Contrib] Django IAM Migration, 整合iam模型migration到Django Migration
- [Contrib] Resource API Framework, 协助构建需要提供给IAM调用的Resource API
- [Contrib] 支持tastypie

## Getting started

### Installation

```
$ pip install bk-iam
```

### Usage

- [usage doc](usage.md)

## Roadmap

- [release log](release.md)

## Support

- [bk forum](https://bk.tencent.com/s-mart/community)
- [bk DevOps online video tutorial(In Chinese)](https://cloud.tencent.com/developer/edu/major-100008)
- Contact us, technical exchange QQ group:

<img src="https://github.com/Tencent/bk-PaaS/raw/master/docs/resource/img/bk_qq_group.png" width="250" hegiht="250" align=center />


## BlueKing Community

- [BK-CI](https://github.com/Tencent/bk-ci)：a continuous integration and continuous delivery system that can easily present your R & D process to you.
- [BK-BCS](https://github.com/Tencent/bk-bcs)：a basic container service platform which provides orchestration and management for micro-service business.
- [BK-BCS-SaaS](https://github.com/Tencent/bk-bcs-saas)：a SaaS provides users with highly scalable, flexible and easy-to-use container products and services.
- [BK-PaaS](https://github.com/Tencent/bk-PaaS)：an development platform that allows developers to create, develop, deploy and manage SaaS applications easily and quickly.
- [BK-SOPS](https://github.com/Tencent/bk-sops)：an lightweight scheduling SaaS  for task flow scheduling and execution through a visual graphical interface. 
- [BK-CMDB](https://github.com/Tencent/bk-cmdb)：an enterprise-level configuration management platform for assets and applications.

## Contributing

If you have good ideas or suggestions, please let us know by Issues or Pull Requests and contribute to the Blue Whale Open Source Community.

If you are interested in contributing, check out the [CONTRIBUTING.md], also join our [Tencent OpenSource Plan](https://opensource.tencent.com/contribution).


## License

Based on the MIT protocol. Please refer to [LICENSE](LICENSE.txt)
