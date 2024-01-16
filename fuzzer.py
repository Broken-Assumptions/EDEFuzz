from argparse import ArgumentParser
import cache
import engine
import mutate
import verify
from constants import *
import logging
from concurrent.futures import ThreadPoolExecutor
import re
import database
import report
import datetime
from pathlib import Path


def fuzz(params):
    mutation, ca, args, logger = params

    try:
        db = database.Connection(args.target)
    except Exception as e:
        logger.error(
            "Cannot connect to database when executing the mutant: "
            + str(mutation)
        )
        logger.error(str(e))
        #del mutation # added to see if this helps reducing memory usage
        return

    # if the same mutation has been executed, pass
    try:
        if db.record_exist(1, str(mutation), None):
            logger.info(
                "The following mutant has been executed in the past: "
                + str(mutation)
            )
            #del mutation # added to see if this helps reducing memory usage
            return
    except Exception as e:
        logger.error(
            "Failed to check if the mutant is executed: "
            + str(mutation)
        )
        logger.error(str(e))
        #del mutation # added to see if this helps reducing memory usage
        return

    try:
        mutation_source = engine.runInstance(ca, mutation, firefox=args.firefox)
        logger.info(
            "Completed executing the following mutant: "
            + str(mutation)
        )
        if mutation:
            db.add_row(1, str(mutation), None, mutation_source)
        else:  # baseline test case
            db.add_row(0, None, None, mutation_source)
    except Exception as e:
        logger.error(
            "The following mutant triggered an error during execution: "
            + str(mutation)
        )
        logger.error(str(e))
    #del mutation # added to see if this helps reducing memory usage
    progress(None)


def run(args):
    if not args.nonheadless:
        SELENIUM_OPTIONS_CHROME.add_argument("--headless=new")
    if args.mode == "c":  # config
        cache.generateCache(args.target, firefox=args.firefox)
        print("Complete. Request-response cache generated in tests/" + args.target + ".data")
    elif args.mode == "f":  # fuzz
        ca = cache.loadCache(args.target)
        response = ca["response"]["body"]
        response_header = ca["response"]["header"]

        # print current time as string

        timestr = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        logpath = (
            Path(".")
            / Path("log")
            / Path("edefuzz-{}-{}.log".format(args.target, timestr))
        )
        #logging.basicConfig(
        #    format='[%(asctime)s][%(levelname)s] %(message)s',
        #    datefmt='%Y-%m-%d %H:%M:%S')
        logger = logging.getLogger("log")
        logger.setLevel(args.verbosity * 10)
        ch = logging.FileHandler(logpath)
        ch.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(ch)

        global tests_total, tests_done
        tests_total = sum(1 for _ in mutate.leaf(response)) + 2
        tests_done = 0

        print(
        "Executing test cases. Progress: 0/"
        + str(tests_total)
        + " (0.00%)  ", end="\r"
    )

        executor = ThreadPoolExecutor(args.thread)

        executor.submit(
            fuzz,
            (
                [],
                ca,
                args,
                logger
            ),
        )  # baseline

        for mutation in mutate.leaf(response):
            executor.submit(
                fuzz,
                (
                    mutation,
                    ca,
                    args,
                    logger
                ),
            )

        executor.submit(
            fuzz,
            (
                [],
                ca,
                args,
                logger
            ),
        )  # baseline (another time)

    elif args.mode == "r":  # report
        db = database.Connection(args.target)
        if args.iattribute:
            report.report(args.target, local_opt_filter=1)
        elif args.iclass:
            report.report(args.target, local_opt_filter=2)
        else:
            report.report(args.target)
    
    elif args.mode == "v":  # verify
        verify.verify(args.target)
    
    elif args.mode == "d":  # delete results from database
        db = database.Connection(args.target)
        db.clear()

def progress(r):
    global tests_done
    tests_done += 1
    print(
        "Executing test cases. Progress: "
        + str(tests_done)
        + "/"
        + str(tests_total)
        + " ("
        + str(round(tests_done / tests_total * 100, 2))
        + "%)  ", end="\r"
    )

if __name__ == "__main__":
    print(
        r"""
      __        __        __        __                              
     /\ \      /\ \      /\ \      /\ \      __       __       __    
    /::\ \    /::\ \    /::\ \    /::\ \    /\_\     /\ \     /\ \   
   /:/\:\ \  /:/\:\ \  /:/\:\ \  /:/\:\ \  /:/ /_    \:\ \    \:\ \  
  /::\ \:\ \/:/ /\:\ \/::\ \:\ \/::\ \:\ \/:/ /\_\____\:\_\____\:\_\ 
 /:/\:\ \:\_\/_/  \:\_\/\:\ \:\_\/\:\ \:\_\/ /:/ /:_____/_/:_____/_/ 
 \:\ \:\_\/_/\ \  /:/ /\ \:\ \/_/_/\:\ \/_/\/:/ /\:\ \    \:\ \      
  \:\ \/_/  \:\_\/:/ /\:\ \:\_\     \:\_\ \::/ /  \:\_\    \:\_\     
   \:\ \     \____/_/  \:\ \/_/      \/_/  \/_/    \/_/     \/_/     
    \:\_\               \:\_\                                       
     \/_/                \/_/                                       
"""
    )
    parser = ArgumentParser(
        description="EDEFuzz - Automatically detect unused data fields in web API response."
    )
    parser.add_argument(
        "mode",
        metavar="MODE",
        help="specify the mode to run: (c)ache, (f)uzz, (r)eport",
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        help="the name of the configuration file to be processed, stored at config/*.config",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        dest="verbosity",
        type=int,
        default=3,
        help="logging level: error4, warning3, info2, debug1",
        metavar="4|3|2|1",
    )
    parser.add_argument(
        "-t",
        "--thread",
        dest="thread",
        type=int,
        default=1,
        help="nubmer of concurrent web browsers opened in the fuzzing phase (default: 1)",
        metavar="N",
    )
    parser.add_argument(
        "-F",
        "--firefox",
        dest="firefox",
        action="store_true",
        help="use Firefox instead of Chrome",
    )
    parser.add_argument(
        "-IC",
        "--ignore-class",
        dest="iclass",
        action="store_true",
        help="remove class attributes from HTML",
    )
    parser.add_argument(
        "-IA",
        "--ignore-all-attributes",
        dest="iattribute",
        action="store_true",
        help="remove all tag attributes from HTML",
    )
    parser.add_argument(
        "-NH",
        "--non-headless",
        dest="nonheadless",
        action="store_true",
        help="Launch web browser in non-healess mode",
    )

    args = parser.parse_args()

    run(args)
