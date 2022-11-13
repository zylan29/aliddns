# aliddns

## 说明

1. 同时支持IPv4和IPv6
2. 自动探测本地IP和公网IP，只有当二者一致时才可能将其添加到解析记录中 
3. 支持定义RR列表，默认为'@'和'*'
4. 如果当前域名没有解析记录，则添加该域名的`@`解析记录
5. 如果当前域名有解析记录，但记录的IP与探测到的IP不符，则更新该条记录
6. 当没有公网IP时，可以使用-l开关开启使用本地IP模式

## 依赖

基于阿里云DNS产品实现的DDNS命令行工具及python库

1. 在阿里云购买域名并完成实名认证
2. 具备管理云解析(DNS)权限的`AccessKey ID`及`AccessKey Secret`

## 安装

### 发布版安装

1. 下载发布版

2. 安装
```shell
pip install aliddns-1.0.3-py3-none-any.whl
```


### 源码安装

```shell
git clone https://github.com/zylan29/aliddns.git

cd aliddns

pip install .
```

安装完成后可使用`aliddns`命令，可通过`whereis aliddns`查询该命令安装位置。

## 使用

### 单次使用

```
usage: aliddns [-h] [-k ACCESSKEY_ID] [-s ACCESSKEY_SECRET] [-d DOMAIN_NAME]
               [-r RESOURCE_RECORDS [RESOURCE_RECORDS ...]] [-l] [--region-id REGION_ID]

Ali DDNS command-line tool.

optional arguments:
  -h, --help            show this help message and exit
  -k ACCESSKEY_ID, --accesskey-id ACCESSKEY_ID
                        AccessKey ID
  -s ACCESSKEY_SECRET, --accesskey-secret ACCESSKEY_SECRET
                        AccessKey secret
  -d DOMAIN_NAME, --domain-name DOMAIN_NAME
                        Your domain name
  -r RESOURCE_RECORDS [RESOURCE_RECORDS ...], --resource-records RESOURCE_RECORDS [RESOURCE_RECORDS ...]
                        Your resource record, e.g. @ *
  -l, --local-ip        Whether use local IP or not, default to NO
  --region-id REGION_ID
                        Region ID
```

参数说明：
```
-k 你的AccessKey ID
-s 你的AccessKey secret
-d 你的域名
-r RR，以空格间隔的列表，默认为'@'和'*'
-l 允许解析到本地IP
--region-id Region ID，默认为cn-hangzhou
```

### 定时任务

使用`crontab`设置定时任务
```shell
crontab -u 你的用户名 -e
```
添加如下内容
```
0 * * * * '到aliddns命令的绝对路径' -k '你的AccessKey ID' -s '你的AccessKey secret' -d '你的域名' >> '输出日志文件'
```
上述配置实现每小时执行一次aliddns