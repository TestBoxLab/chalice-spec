class EventConverter:
    def convert_request(self, event: dict) -> dict:
        """
        parse event input to other type parameter.

        :param event: dict api gateway event
        :return: other type event
        """
        return event

    def convert_response(self, event: dict, response: dict) -> dict:
        """
        parse event response to other type response.

        :param event: dict api gateway event
        :param response: dict api gateway response
        :return: other type response
        """
        return response
