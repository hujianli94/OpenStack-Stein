# OpenStack-Stein

| 服务名称                      | 作用描述                                                       | API 框架                     | 数据库框架                     | 备注               |
|----------------------------|------------------------------------------------------------|----------------------------|----------------------------|------------------|
| aodh                  | 提供告警服务，用于监控和告警系统                                 | Pecan                      | SQLAlchemy + Alembic           |                  |
| barbican              | 提供密钥管理服务，用于管理加密密钥                              | Pecan                       | SQLAlchemy + Alembic                     |                  |
| blazar                | 提供资源预订管理服务，支持云资源的预订                          | v1: Flask；v2: Pecan                       | SQLAlchemy + Alembic |                  |
| ceilometer           | 提供计量和监控服务，用于收集资源使用数据                        | 无                      | sqlalchemy-migrate           |                  |
| cinder               | 提供块存储服务，管理虚拟机的磁盘存储                           | Paste+webob+routes          | sqlalchemy-migrate |                  |
| cloudkitty            | 提供云资源计费系统，用于管理计费数据                           | Pecan                      | SQLAlchemy + Alembic |                  |
| designate             | 提供 DNS 服务，用于域名解析和管理                             | Paste+webob+routes | sqlalchemy-migrate |                  |
| ec2-api               | 提供 EC2 兼容的 API 服务，支持 OpenStack 和 AWS EC2 的互通        | Paste+webob+routes          | sqlalchemy-migrate           |                  |
| freezer               | 提供备份和恢复服务                                            | 无                       | 无（依赖其他服务） |                  |
| freezer-api           | Freezer 服务的 API 接口                                        | Paste+webob+routes     | sqlalchemy-migrate |                  |
| freezer-dr            | Freezer 数据恢复服务                                          | 无                      | 无（依赖其他服务） |                  |
| glance               | 提供镜像服务，用于存储和管理虚拟机镜像                         | Paste+webob+routes    | SQLAlchemy + Alembic |                  |
| horizon              | 提供 Web 用户界面前端服务，用于管理 OpenStack 资源             | Django                      | 无（依赖其他服务） |                  |
| ironic               | 提供裸金属服务，支持物理服务器的管理                           | Pecan                      | SQLAlchemy + Alembic |                  |
| karbor                | 提供灾难恢复服务                                               | Paste+webob+routes     | sqlalchemy-migrate |                  |
| keystone             | 提供身份认证服务，用于管理 OpenStack 资源的身份验证和访问控制  | Flask   | SQLAlchemy + Alembic |                  |
| magnum                | 提供容器管理服务，用于管理 Kubernetes 和 Docker 集群             | Pecan                  | SQLAlchemy + Alembic |                  |
| manila                | 提供共享文件系统服务，支持多种类型的共享存储资源              | Paste+webob+routes     | SQLAlchemy + Alembic |                  |
| masakari              | 提供故障保护和恢复服务                                         | Paste+webob+routes    | sqlalchemy-migrate |                  |
| mistral               | 提供工作流引擎服务，支持自动化任务管理                         | Pecan                  | SQLAlchemy + Alembic |                  |
| monasca-api           | 提供监控和报警的 API 服务                                       | Paste+webob+routes     | SQLAlchemy + Alembic |                  |
| monasca-events-api    | 提供事件管理的 API 接口                                         | Paste+webob+routes     | 无（依赖其他服务） |                  |
| monasca-log-api       | 提供日志服务，支持集中式日志管理                               | Paste+webob+routes     | 无（依赖其他服务） |                  |
| murano                | 提供应用程序市场服务，支持云应用程序的发布和管理              | Paste+webob+routes     | SQLAlchemy + Alembic |                  |
| neutron              | 提供网络服务，管理虚拟网络、子网、路由等                         | Paste+webob+routes          | SQLAlchemy + Alembic |                  |
| nova                 | 提供计算服务，管理虚拟机的创建、调度和生命周期                 | Paste+webob+routes    | sqlalchemy-migrate           |                  |
| octavia               | 提供负载均衡服务，支持 Layer 4 和 Layer 7 负载均衡                | Pecan                  | SQLAlchemy + Alembic |                  |
| openstack-congress    | 提供策略和合规性服务，支持 OpenStack 环境的策略定义和管理      | Paste+webob+routes    | sqlalchemy-migrate           |                  |
| openstack-cyborg      | 提供硬件加速服务，支持 FPGA 等硬件资源的管理                   | Pecan                  | SQLAlchemy + Alembic |                  |
| openstack-heat       | 提供 Orchestration 服务，支持通过模板自动化资源的管理          | Paste+webob+routes    | sqlalchemy-migrate |                  |
| openstack-placement   | 提供资源调度服务，支持计算、存储和网络资源的高效调度          | Paste+webob+routes    | SQLAlchemy + Alembic               |                  |
| panko                 | 提供事件监控和存储服务，支持 OpenStack 环境中的事件处理        | Pecan                  | SQLAlchemy + Alembic |                  |
| python-watcher        | 提供自动化监控和资源管理服务                                   | Pecan                      | sqlalchemy-migrate           |                  |
| qinling               | 提供函数计算服务，支持无服务器计算框架                         | Pecan                  | SQLAlchemy + Alembic |                  |
| sahara               | 提供大数据处理服务，支持 Hadoop、Spark 等大数据框架            | Flask            | sqlalchemy-migrate           |                  |
| searchlight           | 提供搜索和数据分析服务                                         | Paste+webob+routes     | SQLAlchemy + Alembic+Elasticsearch |                  |
| senlin                | 提供集群管理服务，支持 OpenStack 资源的自动化管理              | Paste+webob+routes     | sqlalchemy-migrate |                  |
| solum                 | 提供云应用生命周期管理服务                                     | Pecan                  | SQLAlchemy + Alembic |                  |
| storlets              | 提供存储服务扩展，支持存储的插件式开发                         | 无独立API（嵌入Swift）       | 无（依赖Swift） |                  |
| swift                | 提供对象存储服务，支持海量数据的存储                           | Paste+webob+routes          | SQLAlchemy + Alembic |                  |
| tacker                | 提供网络功能虚拟化（NFV）管理服务                              | Pecan                  | SQLAlchemy + Alembic |                  |
| tricircle            | 提供跨多个数据中心的网络服务                                   | Pecan | sqlalchemy-migrate |                  |
| trove                | 提供数据库服务，支持多种数据库管理                              | Paste+webob+routes     | sqlalchemy-migrate |                  |
| vitrage               | 提供智能监控和分析服务，支持资源的异常检测和预测               | Pecan                  | SQLAlchemy + Alembic |                  |
| zaqar                 | 提供消息队列服务，用于处理异步消息                             | Paste+webob+routes     | SQLAlchemy + Alembic |                  |
| zun                   | 提供容器管理服务，支持容器生命周期管理                         | Pecan                  | SQLAlchemy + Alembic |                  |

源码:

- https://github.com/FuzeSoft/OpenStack-Stein.git
