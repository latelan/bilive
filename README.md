Bilive
======

向B站发心跳包，实现24h挂机看直播，获得经验值

* Linux
* Python 2.x

$crontab -e

`
*/6 * * * * python ./bilive.py > ./bilive.log
`

Thanks to [lwl12](https://blog.lwl12.com/)
