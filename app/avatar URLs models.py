from hashlib import md5


# ...
# todo add this to the user object
class User(UserMixin, db.Model):
    # ...
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.cs2005group.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
