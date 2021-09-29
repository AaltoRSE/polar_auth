from .user_test_case import UserTestCase
from django.test.client import RequestFactory
from django.contrib.admin.sites import AdminSite
from users.models import User, Subscriber
from users.admin import CustomUserAdmin, SubscriberAdmin
from polar_auth.settings import data_folder


class UserAdminTestCase(UserTestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = RequestFactory()

    def test_user_admin(self):
        ''' Checks that list of actions contains admin_email and
            does not contain delete_selected
        '''
        # Log in as the admin user
        self.client.login(
            username=self.user1_data['email'],
            password=self.user1_data['password']
        )

        # Create the admin page and run get_actions
        admin = CustomUserAdmin(model=User, admin_site=AdminSite())
        request = self.request_factory.get('/')
        request.user = self.user1
        actions = admin.get_actions(request)

        # Check that the actons
        assert 'delete_selected' not in actions
        assert 'admin_email' in actions

    def test_received_data(self):
        ''' Checks that list of actions contains admin_email and
            does not contain delete_selected
        '''
        # Log in as the admin user
        self.client.login(
            username=self.user1_data['email'],
            password=self.user1_data['password']
        )

        # Write the ids with data file
        correct_ids = [423, 53642, 213, self.user1.user_id]
        with open(data_folder + '/ids_with_data', 'w') as id_file:
            for id in correct_ids:
                id_file.write(f'{id} 2021-01-01\n')

        # Create the admin page and run get_actions
        admin = CustomUserAdmin(model=User, admin_site=AdminSite())
        date = admin.get_received_data(self.user1)

        # The data_received_date now should be set to 2021-01-01
        assert self.user1.data_received_date == date


class SubscriberAdminTestCase(UserTestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = RequestFactory()

    def test_subscriber_admin(self):
        ''' Checks that list of actions contains admin_email and
            does not contain delete_selected
        '''
        # Log in as the admin user
        self.client.login(
            username=self.user1_data['email'],
            password=self.user1_data['password']
        )

        # Create the admin page and run get_actions
        admin = SubscriberAdmin(model=Subscriber, admin_site=AdminSite())
        request = self.request_factory.get('/')
        request.user = self.user1
        actions = admin.get_actions(request)

        # Check that the actons
        assert 'delete_selected' not in actions
        assert 'admin_email' in actions

