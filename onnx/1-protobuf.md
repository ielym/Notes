# 1 介绍

## 1.1 背景

Protobuf （Protocol Buffer）是谷歌内部的混合语言数据标准，用于将结构化的数据进行序列化。Protobuf与Json类似，但是比Json更快，更小。可用于数据存储、通讯协议等领域。

**Github** : [protocolbuffers/protobuf](https://github.com/protocolbuffers/protobuf)

**Document** : [protocol-buffers/](https://developers.google.com/protocol-buffers/)

## 1.2 特点

+ 语言无关
+ 平台无关
+ 可扩展



# 2 Python

## 2.1 字段类型

+ `optional` : 可以不设置该字段。如果不设置，可以自定义默认值，或者系统默认设置：`int : 0`, `string : ""`，`bool : false` 。
+ `repeated` : 字段可以重复多次。可看作为动态数组。
+ `required` : 必须提供该字段的值。

```
syntax = "proto2";

package tutorial;

message Person {
  optional string name = 1;
  optional int32 id = 2;
  optional string email = 3;

  enum PhoneType {
    MOBILE = 0;
    HOME = 1;
    WORK = 2;
  }

  message PhoneNumber {
    optional string number = 1;
    optional PhoneType type = 2 [default = HOME];
  }

  repeated PhoneNumber phones = 4;
}

message AddressBook {
  repeated Person people = 1;
}
```

