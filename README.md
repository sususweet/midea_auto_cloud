# Midea Auto Cloud
 
 [![Stable](https://img.shields.io/github/v/release/sususweet/midea-meiju-codec)](https://github.com/sususweet/midea-meiju-codec/releases/latest)

通过网络获取你美居家庭中的设备，并且通过美的云端进行控制。

- 自动查找和发现设备
- 自动下载设备的协议文件
- 将设备状态更新为设备可见的属性

## 非常初期的预览版

- 仅供技术实现验证以及评估
- 所有设备默认可生成一个名为Status的二进制传感器，其属性中列出了设备可访问的所有属性，当然有些值不可设置
- Status实体前几项列出了该设备的分类信息，供参考

## 实体映射

映射文件位于`device_mapping`下, 每个大的品类一个映射文件，目前支持映射的实体类型如下:
- sensor
- binary_sensor
- switch
- select
- climate
- fan
- water_heater

示例配置`22012227`演示了如何将设备属性映射成以上各种HomeAssistant中的实体。

