import logging
import os
import subprocess

from django.core.management import call_command
from django.db import connections
from django.test.runner import DiscoverRunner
from django.conf import settings

logger = logging.getLogger(__name__)

TEST_DUMP_LOCATION = os.path.join(os.path.dirname(__file__), 'testdb.dump')


class SnapshotDBRunnerMixin(object):
    def setup_databases(self, *args, **kwargs):
        db_settings = connections['default'].settings_dict
        if db_settings['TEST']['NAME']:
            db_settings['NAME'] = db_settings['TEST']['NAME']
        else:
            db_settings['NAME'] = 'test_' + db_settings['NAME']

        from django.core import management

        original_call_command = management.call_command

        def hijacked_call_command(name, *args, **options):
            if name == 'migrate':
                connection_data = connections['default'].settings_dict.copy()

                environ = os.environ.copy()
                environ['PGPASSWORD'] = connection_data['PASSWORD']
                connection_data['FILE'] = TEST_DUMP_LOCATION

                # postgres specific
                command = (
                    'pg_restore -d %(NAME)s -U %(USER)s -h %(HOST)s '
                    '%(FILE)s.dump' % (connection_data))
                try:
                    print(command)
                    subprocess.check_output(command.split(), env=environ,
                                            stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError, e:
                    raise Exception(
                        u"Couldn't load database dump. Reason:\n%s" % e.output)

                # call migrate removing not relevant arguments to continue
                # with the migration
                options.pop('test_flush', None)
                return original_call_command('migrate', *args, **options)
            else:
                return original_call_command(name, *args, **options)

        management.call_command = hijacked_call_command
        old_names, mirrors = super(SnapshotDBRunnerMixin,
                                   self).setup_databases(*args, **kwargs)
        management.call_command = original_call_command

        # Force destroying db right after tests run (or not)
        if 'DJANGO_SNAPSHOT_DB_RUNNER_DESTROYDB_AFTER_RUN' in os.environ:
            destroy_db_after_run = bool(int(
                os.environ['DJANGO_SNAPSHOT_DB_RUNNER_DESTROYDB_AFTER_RUN']
            ))
            old_names = [(o[0], o[1], destroy_db_after_run) for o in old_names]

        return old_names, mirrors


class SnapshotDBRunner(SnapshotDBRunnerMixin, SkipBlacklistMixin, DiscoverRunner):
    pass


try:
    from django_nose import NoseTestSuiteRunner

    class DjangoNoseTestSuiteSnapshotDBRunner(SnapshotDBRunnerMixin,
                                              NoseTestSuiteRunner):
        pass
except ImportError:
    logger.info(
        'The test runner DjangoNoseTestSuiteSnapshotDBRunner is not available '
        'as django_nose is not installed')