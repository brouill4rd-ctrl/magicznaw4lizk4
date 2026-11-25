import asyncio
import tempfile
import unittest
from pathlib import Path

from database import Database


class DatabaseTests(unittest.TestCase):
    def test_duplicate_stacks_persist_and_only_one_wins(self):
        async def run():
            with tempfile.TemporaryDirectory() as directory:
                db = Database(Path(directory) / "game.sqlite3")
                await db.connect()
                await db.execute("INSERT INTO creatures(id,name,aliases,rarity,image_path) VALUES(1,'Niuchacz','[]','uncommon','niffler.png')")
                encounter = await db.spawn(10, 20, 1, 120)
                self.assertIsNotNone(encounter)
                winners = await asyncio.gather(db.catch(encounter, 30), db.catch(encounter, 31))
                self.assertEqual(sum(winners), 1)
                next_encounter = await db.spawn(10, 20, 1, 120)
                self.assertTrue(await db.catch(next_encounter, 30))
                quantity = await db.one("SELECT quantity FROM user_creatures WHERE discord_id=30 AND creature_id=1")
                total = await db.one("SELECT total_captures FROM users WHERE discord_id=30")
                self.assertEqual(quantity["quantity"], 2)
                self.assertEqual(total["total_captures"], 2)
                await db.close()
        asyncio.run(run())

    def test_data_survives_restart_and_servers_have_separate_settings(self):
        async def run():
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "game.sqlite3"
                db = Database(path)
                await db.connect()
                await db.execute("INSERT INTO creatures(id,name,aliases,rarity,image_path) VALUES(1,'Niuchacz','[]','uncommon','niuchacz.JPG')")
                await db.catch(await db.spawn(100, 200, 1, 120), 300)
                await db.settings(100)
                await db.execute("UPDATE server_settings SET spawn_min_messages=7 WHERE guild_id=100")
                await db.close()

                reopened = Database(path)
                await reopened.connect()
                self.assertEqual((await reopened.one("SELECT quantity FROM user_creatures WHERE discord_id=300"))["quantity"], 1)
                self.assertEqual((await reopened.settings(100))["spawn_min_messages"], 7)
                self.assertEqual((await reopened.settings(101))["spawn_min_messages"], 20)
                await reopened.close()
        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
