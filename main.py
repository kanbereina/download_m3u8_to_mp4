import os
import asyncio
from pathlib import Path

import httpx
from loguru import logger



base_path = Path(__file__).parent
database = base_path/"database"
timeout = httpx.Timeout(timeout=None)


class File:
    @staticmethod
    def create_first_dir(dir_path: Path):
        """
        创建文件目录
        :param dir_path: 文件目录
        :return: True-创建目录成功 None-目录已存在
        """
        if not os.path.exists(dir_path):
            logger.info(f"目录缺失,创建路径于{dir_path}")
            os.mkdir(dir_path)


File.create_first_dir(base_path)


class DownloadM3U8:
    @staticmethod
    async def get_m3u8_ts_list(client: httpx.AsyncClient, url: str) -> list[str]:
        """获得index.m3u8文件中.ts文件的名称列表"""
        raw_data = await client.get(url)
        return [item for item in (raw_data.text.split("\n")) if ".ts" in item]

    @staticmethod
    def reload_ts_url(m3u8_url: str, ts_list: list[str]) -> list[str]:
        """获得.ts文件下载地址列表"""
        return [m3u8_url.replace("index.m3u8", item) for item in ts_list]

    @staticmethod
    async def get_ts_data(client: httpx.AsyncClient, ts_urls: list[str]) -> bytes:
        """合并.ts文件的下载数据"""
        async def download_data(url: str) -> bytes:
            logger.info(f"正在从'{url}'下载数据...")
            return (await client.get(url=url, timeout=timeout)).content
        tasks = [await asyncio.create_task(download_data(ts_url)) for ts_url in ts_urls]
        logger.success("成功合并数据！")
        return b"".join(tasks)

    @staticmethod
    def write_ts_data(ts_data: bytes, file_name: str) -> Path:
        with (path := database/(name := f"{file_name}.mp4")).open("wb") as f:
            f.write(ts_data)
        logger.success(f"存储'{name}'文件于：{path}")
        return path


async def download_main(m3u8_url: str, file_name: str) -> None:
    File.create_first_dir(database)  # 初始化目录
    logger.info(f"开始从'{m3u8_url}'下载视频...")
    async with httpx.AsyncClient() as client:
        ts_list = await DownloadM3U8.get_m3u8_ts_list(client, m3u8_url)
        ts_urls = DownloadM3U8.reload_ts_url(m3u8_url, ts_list)
        data = await DownloadM3U8.get_ts_data(client, ts_urls)
        DownloadM3U8.write_ts_data(data, file_name)
    logger.success(f"文件'{file_name}.mp4'下载完成！")



if __name__ == "__main__":
    File.create_first_dir(base_path)
    m3u8_url1 = "example.com/index.m3u8"
    file_name1 = "example"
    asyncio.run(download_main(m3u8_url1, file_name1))
