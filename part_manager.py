# part_manager.py
from logger_setup import logger


class PartManager:

    def __init__(self, part_repo):
        self.part_repo = part_repo

    def get_part_config(self, part_name):
        return self.part_repo.get_by_name(part_name)

    def part_exists(self, part_name):
        return self.part_repo.get_by_name(part_name) is not None

    def get_all_parts(self):
        return self.part_repo.get_all()

    def add_part_config(self, part, km_life, month_life, km_limit, day_limit):
        if self.part_repo.get_by_name(part):
            logger.warning(f"Part already exists: {part}")
            return False, "Part already exists."

        created = self.part_repo.create_part(part, km_life, month_life, km_limit, day_limit)
        if not created:
            logger.warning(f"Part already exists: {part}")
            return False, "Part already exists."

        logger.info(f"Part config added: {part}")
        return True, "Part added successfully."

    def update_part_config(self, part, km_life, month_life, km_limit, day_limit):
        existing = self.part_repo.get_by_name(part)
        if not existing:
            logger.warning(f"Part not found: {part}")
            return False, "Part not found."

        self.part_repo.update_part(existing, km_life, month_life, km_limit, day_limit)
        logger.info(f"Part config updated: {part}")
        return True, "Part updated successfully."

    def delete_part_config(self, part):
        existing = self.part_repo.get_by_name(part)
        if not existing:
            logger.warning(f"Part not found: {part}")
            return False, "Part not found."

        # Deleting a part that is in use would silently wipe the maintenance
        # records of every user's cars, so it is refused.
        used = self.part_repo.count_usage(existing.id)
        if used:
            logger.warning(f"Part {part} is in use by {used} record(s); not deleted")
            return False, f"Part is in use by {used} record(s) and cannot be deleted."

        self.part_repo.delete_part(existing)
        logger.info(f"Part config deleted: {part}")
        return True, "Part deleted successfully."
