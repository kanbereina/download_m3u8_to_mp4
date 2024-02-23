# download_m3u8_to_mp4
一个简易的通过爬虫获得的index.m3u8文件下载未加密的m3u8视频的python程序


必要的Python软件包：
1. httpx
2. loguru（为方便显示日志，不使用的话可以把源码logger.xxx部分改成print）




注：
如果有多个index.m3u8文件下载视频的需求，可以再次用asyncio.create_task()方法增加下载效率
