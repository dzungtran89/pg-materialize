import unittest

from pg_materialize.pg_materialize import extract_nodes


class PgMaterializeTest(unittest.TestCase):

    def test_extract_nodes(self):

        query = """
            BEGIN;

              CREATE MATERIALIZED VIEW IF NOT EXISTS schema1.messages_mv
              AS (
                SELECT
                  DATE(e.created_on) AS creation_date,
                  m.account_id
                FROM schema1.events_mv e
                INNER JOIN schema2.members_mv m
                  ON e.member_id = m.id
                LEFT JOIN schema3.log_mv l
                  ON l.event_id = e.id
                WHERE e.event_type = 'TEST'
                GROUP BY creation_date, m.account_id
                ORDER BY 1, 2 ASC
              ) WITH DATA;

            COMMIT;
        """
    
        actual = extract_nodes(query, '_mv')
        expected = {
            'dependencies': set(['schema3.log_mv', 'schema1.events_mv', 'schema2.members_mv']),
            'views': set(['schema1.messages_mv'])
        }
        self.assertEqual(actual, expected)

        query = """
            CREATE MATERIALIZED VIEW schema1.messages_mv
              AS (
                SELECT
                  DATE(e.created_on) AS creation_date,
                  m.account_id
                FROM (
                  SELECT *
                  FROM schema1.events
                ) e
                INNER JOIN schema2.members m
                  ON e.member_id = m.id
                LEFT JOIN schema3.log_mv l
                  ON l.event_id = e.id
                WHERE e.event_type = 'TEST'
                GROUP BY creation_date, m.account_id
                ORDER BY 1, 2 ASC
              )
        """

        actual = extract_nodes(query, '_mv')
        expected = {
            'dependencies': set(['schema3.log_mv']),
            'views': set(['schema1.messages_mv'])
        }
        self.assertEqual(actual, expected)