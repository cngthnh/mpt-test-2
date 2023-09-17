import os


def handle(*args):
    # run clean_up.sh script, the script is in the same directory as this file
    print("Running post deployment hook")

    os.system(f"sh {os.path.dirname(os.path.realpath(__file__))}/clean_up.sh")

    # run sync_s3.sh script, the script is in the same directory as this file
    os.system(f"sh {os.path.dirname(os.path.realpath(__file__))}/sync_s3.sh {os.getenv('APP_NAME', 'temp')}")
