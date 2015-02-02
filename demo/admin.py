from jclndbadmin import admin


class UserAdmin(admin.ModelAdmin):

    def songs(self):
        pass

    def purchases(self):
        pass

    fields = (
        'first_name',
        'last_name',
        'email',
        songs,
        purchases,
    )

    filters = []
