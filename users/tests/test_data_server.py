from .user_test_case import UserTestCase
from polar_auth.settings import data_folder
import users.data_server as data_server


class DataServerTestCase(UserTestCase):
    def setUp(self):
        super().setUp()

        self.user_id = 2135432

    def test_communicate_token(self):
        # Count current tokens
        with open(data_folder + '/new_tokens') as token_file:
            num_lines_at_start = len(token_file.readlines())

        # Communicat the tokens
        data_server.communicate_token('id', 'token', self.user_id)

        # Check the last line is correct and that one has been added
        with open(data_folder + '/new_tokens') as token_file:
            lines = token_file.readlines()
            assert(len(lines) == num_lines_at_start+1)
            correct_line = f'token id {self.user_id}\n'
            self.assertEqual(lines[-1], correct_line)

    def test_delete_token(self):
        # Count current ids
        with open(data_folder + '/delete_tokens') as token_file:
            num_lines_at_start = len(token_file.readlines())

        # Communicate the ids
        data_server.delete_token(self.user_id)

        # Check the last line is correct and that one has been added
        with open(data_folder + '/delete_tokens') as token_file:
            lines = token_file.readlines()
            assert(len(lines) == num_lines_at_start+1)
            correct_line = f'{self.user_id}\n'
            self.assertEqual(lines[-1], correct_line)

    def test_get_ids_with_data(self):
        # Write some IDs into the file
        correct_ids = [423, 53642, 213]
        with open(data_folder + '/ids_with_data', 'w') as id_file:
            for id in correct_ids:
                id_file.write(f'{id} date\n')

        # read the file
        ids = data_server.get_ids_with_data()

        # Check the ids are correct
        for id1, idline in zip(correct_ids, ids):
            self.assertEqual(id1, idline[1])

