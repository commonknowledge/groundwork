import os
import re
import sys


def get_version(ref_name):
    if ref_name:
        ref_match = re.search(r"v(\d+)\.(\d+)\.(\d+)$", ref_name)
        if ref_match is None:
            return ()

        return ref_match.groups()


if __name__ == "__main__":
    print(".".join(get_version(os.getenv("GITHUB_REF_NAME"))))
