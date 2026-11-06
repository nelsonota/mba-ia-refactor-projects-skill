from src.services import report_service


class ReportController:
    @staticmethod
    def summary_report(data=None, query_args=None):
        return report_service.summary_report(data=data, query_args=query_args)

    @staticmethod
    def user_report(user_id=None, data=None, query_args=None):
        return report_service.user_report(user_id=user_id, data=data, query_args=query_args)

    @staticmethod
    def get_categories(data=None, query_args=None):
        return report_service.get_categories(data=data, query_args=query_args)

    @staticmethod
    def create_category(data=None, query_args=None):
        return report_service.create_category(data=data, query_args=query_args)

    @staticmethod
    def update_category(category_id=None, data=None, query_args=None):
        return report_service.update_category(category_id=category_id, data=data, query_args=query_args)

    @staticmethod
    def delete_category(category_id=None, data=None, query_args=None):
        return report_service.delete_category(category_id=category_id, data=data, query_args=query_args)
