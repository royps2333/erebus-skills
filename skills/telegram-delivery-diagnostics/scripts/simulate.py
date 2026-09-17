#!/usr/bin/env python3
"""Offline delivery uncertainty fixture; no credentials or network access."""
import json
from pathlib import Path
import sqlite3
import tempfile


class Queue:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS jobs (
                key TEXT PRIMARY KEY, reply TEXT, state TEXT NOT NULL,
                generations INTEGER NOT NULL DEFAULT 0, receipt INTEGER);
        ''')

    def accept(self, key):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO jobs(key,state) VALUES (?, 'accepted')", (key,))

    def generate(self, key, fail=False):
        if fail:
            raise RuntimeError('synthetic generation failure')
        with self.db:
            self.db.execute("UPDATE jobs SET reply='Synthetic reply',state='ready',generations=generations+1 WHERE key=? AND state='accepted'", (key,))

    def state(self, key):
        return self.db.execute('SELECT state,generations,receipt FROM jobs WHERE key=?', (key,)).fetchone()

    def send(self, key, remote, fault=None, unknown_policy='hold'):
        if unknown_policy not in ('hold', 'retry'):
            raise ValueError('invalid policy')
        with self.db:
            if unknown_policy == 'retry':
                self.db.execute("UPDATE jobs SET state='ready' WHERE key=? AND state IN ('sending','unknown')", (key,))
            claimed = self.db.execute("UPDATE jobs SET state='sending' WHERE key=? AND state='ready'", (key,)).rowcount
        if not claimed:
            return self.state(key)[0]
        if fault == 'crash_before_send':
            return 'sending'
        if fault == 'rejected':
            with self.db:
                self.db.execute("UPDATE jobs SET state='ready' WHERE key=?", (key,))
            return 'ready'  # Proven nonacceptance in this synthetic transport only.
        remote.append({'key': key, 'message_id': len(remote) + 1})
        receipt = remote[-1]['message_id']
        if fault == 'lost_response':
            with self.db:
                self.db.execute("UPDATE jobs SET state='unknown' WHERE key=?", (key,))
            return 'unknown'
        try:
            with self.db:
                self.db.execute("UPDATE jobs SET state='sent',receipt=? WHERE key=?", (receipt, key))
                if fault == 'receipt_rollback':
                    raise RuntimeError('synthetic receipt commit failure')
        except RuntimeError:
            return 'sending'
        return 'sent'

    def close(self):
        self.db.close()


def demo():
    results = []
    for fault in ('lost_response', 'receipt_rollback', 'crash_before_send'):
        for policy in ('hold', 'retry'):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'queue.db'
                remote = []
                q = Queue(path);q.accept('synthetic-bot:update-1');q.generate('synthetic-bot:update-1')
                q.send('synthetic-bot:update-1', remote, fault);q.close()
                q = Queue(path)
                q.send('synthetic-bot:update-1', remote, unknown_policy=policy)
                state, generations, _ = q.state('synthetic-bot:update-1');q.close()
                results.append(dict(fault=fault, policy=policy, local_state=state,
                                    generations=generations, remote_messages=len(remote)))
    return results


if __name__ == '__main__':
    print(json.dumps(demo(), indent=2))
