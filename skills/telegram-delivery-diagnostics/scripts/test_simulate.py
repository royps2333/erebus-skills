import tempfile
from pathlib import Path
import unittest
from simulate import Queue


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'queue.db'
        self.q = Queue(self.path);self.remote = [];self.key = 'bot-a:update-7'
        self.q.accept(self.key)

    def tearDown(self):
        self.q.close();self.tmp.cleanup()

    def restart(self):
        self.q.close();self.q = Queue(self.path)

    def test_duplicate_intake_generates_once(self):
        self.q.accept(self.key);self.q.generate(self.key);self.q.generate(self.key)
        self.assertEqual(self.q.state(self.key)[1], 1)

    def test_bot_scoped_keys_stay_separate(self):
        self.q.accept('bot-b:update-7');self.q.generate(self.key)
        self.assertEqual(self.q.state('bot-b:update-7')[0], 'accepted')

    def test_failed_generation_can_recover(self):
        with self.assertRaises(RuntimeError):self.q.generate(self.key, fail=True)
        self.restart();self.q.generate(self.key);self.q.send(self.key,self.remote)
        self.assertEqual(self.q.state(self.key), ('sent',1,1))

    def test_confirmed_rejection_reuses_saved_reply(self):
        self.q.generate(self.key);self.q.send(self.key,self.remote,'rejected')
        self.assertEqual(len(self.remote),0)
        self.restart();self.q.send(self.key,self.remote)
        self.assertEqual(self.q.state(self.key),('sent',1,1))

    def test_lost_response_held_across_restart(self):
        self.q.generate(self.key);self.q.send(self.key,self.remote,'lost_response')
        self.restart();self.q.send(self.key,self.remote)
        self.assertEqual(len(self.remote),1)
        self.assertEqual(self.q.state(self.key)[0],'unknown')

    def test_retry_lost_response_duplicates_without_regeneration(self):
        self.q.generate(self.key);self.q.send(self.key,self.remote,'lost_response')
        self.restart();self.q.send(self.key,self.remote,unknown_policy='retry')
        self.assertEqual(len(self.remote),2)
        self.assertEqual(self.q.state(self.key),('sent',1,2))

    def test_receipt_rollback_preserves_uncertainty(self):
        self.q.generate(self.key);self.q.send(self.key,self.remote,'receipt_rollback')
        self.restart();self.q.send(self.key,self.remote)
        self.assertEqual(self.q.state(self.key),('sending',1,None))
        self.assertEqual(len(self.remote),1)

    def test_hold_can_omit_unsent_reply(self):
        self.q.generate(self.key);self.q.send(self.key,self.remote,'crash_before_send')
        self.restart();self.q.send(self.key,self.remote)
        self.assertEqual(len(self.remote),0)
        self.assertEqual(self.q.state(self.key)[0],'sending')

    def test_saved_receipt_suppresses_repeat(self):
        self.q.generate(self.key);self.q.send(self.key,self.remote)
        self.restart();self.q.send(self.key,self.remote,unknown_policy='retry')
        self.assertEqual(len(self.remote),1)


if __name__ == '__main__':unittest.main()
