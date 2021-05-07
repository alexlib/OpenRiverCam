import flask_admin as admin


class HelpView(admin.BaseView):
    @admin.expose("/")
    def index(self):
        """
        Specify template for help page.

        :return:
        """
        return self.render("help/index.html")
