from src.services import task_service


class TaskController:
    @staticmethod
    def get_tasks(data=None, query_args=None):
        return task_service.get_tasks(data=data, query_args=query_args)

    @staticmethod
    def get_task(task_id=None, data=None, query_args=None):
        return task_service.get_task(task_id=task_id, data=data, query_args=query_args)

    @staticmethod
    def create_task(data=None, query_args=None):
        return task_service.create_task(data=data, query_args=query_args)

    @staticmethod
    def update_task(task_id=None, data=None, query_args=None):
        return task_service.update_task(task_id=task_id, data=data, query_args=query_args)

    @staticmethod
    def delete_task(task_id=None, data=None, query_args=None):
        return task_service.delete_task(task_id=task_id, data=data, query_args=query_args)

    @staticmethod
    def search_tasks(data=None, query_args=None):
        return task_service.search_tasks(data=data, query_args=query_args)

    @staticmethod
    def task_stats(data=None, query_args=None):
        return task_service.task_stats(data=data, query_args=query_args)
