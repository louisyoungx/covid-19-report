from Core.core import main
from Logger.logger import logger
from Scheduler.scheduler import Timer
from Config.settings import config
from Server.server import server
from threading import Thread
from concurrent.futures import ProcessPoolExecutor

def running():
    PROCESS_MODEL = config.settings("Server", "PROCESS_MODEL")
    SCHEDULER = config.settings("Scheduler", "START_USING")
    SERVER = config.settings("Server", "START_USING")
    if SCHEDULER is False:
        thread_main = Thread(target=main)
        thread_main.start()
    else: # 调度器开启后main函数将被scheduler调度器代理，开启定时执行main
        skipWeekend = config.settings("Scheduler", "SKIP_WEEKEND")
        startTime1 = config.settings("Scheduler", "START_TIME_1")
        startTime2 = config.settings("Scheduler", "START_TIME_2")
        startTime3 = config.settings("Scheduler", "START_TIME_3")
        scheduler1 = Timer(task=main, startTime=startTime1, skipWeekend=skipWeekend)
        scheduler2 = Timer(task=main, startTime=startTime2, skipWeekend=skipWeekend)
        scheduler3 = Timer(task=main, startTime=startTime3, skipWeekend=skipWeekend)
        thread_scheduler1 = Thread(target=scheduler1.schedule)
        thread_scheduler2 = Thread(target=scheduler2.schedule)
        thread_scheduler3 = Thread(target=scheduler3.schedule)
        thread_scheduler1.start()
        thread_scheduler2.start()
        thread_scheduler3.start()
    if SERVER is True:
        if PROCESS_MODEL:
            work_count = config.settings("Server", "PROCESS_COUNT")
            server_process(work_count)
        else:
            thread_server = Thread(target=server)
            thread_server.start()

def server_process(work_count=4):
    with ProcessPoolExecutor(work_count) as pool:
        for i in range(work_count):
            pool.submit(server())

if __name__ == "__main__":
    DEBUG = config.settings("Debug", "DEBUG")
    if DEBUG is True:
        logger.info("\n===== DEBUG MODE =====")
        main()
    else:
        running()

