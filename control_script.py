import argparse
import json
import datetime
import os
import sys
from prettytable import PrettyTable, ALL

from pre_wigs_validation.constants import COLOR_MAP
from pre_wigs_validation.enums import ValidationResult, Colors
from pre_wigs_validation.dataclasses import ValidationOutput
from pre_wigs_validation.instance import ValidationInstance
from pre_wigs_validation.utils import sanitize_json, get_final_result

from pre_wigs_validation.enhanced_networking import EnhancedNetworking
from pre_wigs_validation.free_disk_space import FreeDiskSpace
from pre_wigs_validation.third_party_software import ThirdPartySoftware
from pre_wigs_validation.operating_system import OperatingSystem
from pre_wigs_validation.ssh_configuration import SSHConfiguration
from pre_wigs_validation.yum_repo_access import YumRepoAccess
from pre_wigs_validation.instance_profile import InstanceProfile
from pre_wigs_validation.ssm_agent import SSMAgent


########################
# validation master list
########################
VALIDATION_CLASSES = [
    EnhancedNetworking,
    FreeDiskSpace,
    ThirdPartySoftware,
    OperatingSystem,
    SSHConfiguration,
    YumRepoAccess,
    InstanceProfile,
    SSMAgent,
]


def main() -> int:



    parser = argparse.ArgumentParser(
        description="Validates that a Linux machine is prepared for ingestion into AMS via WIGs"
    )
    parser.add_argument(
        "-l",
        "--log",
        dest="log",
        action="store_true",
        help="create json log file of results in logs folder",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="include in-depth error messages in console output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        help="suppress console output",
    )

    # TODO config path

    args = parser.parse_args()

    cfg_path = "config.json"
    cfg_exists = False
    try:
        with open(cfg_path, "r") as jsonfile:
            cfg = json.load(jsonfile)
            cfg_exists = True
    except FileNotFoundError:
        pass

    instance = ValidationInstance()
    validation_outputs = []
    exit_code = 0
    for validation_class in VALIDATION_CLASSES:

        valid_json = False
        if cfg_exists:
            valid_json = validation_class.__name__ in cfg

        kw_defaults = validation_class.validate.__kwdefaults__
        kw_defaults_json = json.dumps(kw_defaults)
        name = validation_class.__name__

        # TODO quotes around class name, whole thing
        try:
            validation = validation_class()

            if cfg_exists:
                if valid_json:
                    output = validation.validate(**cfg[name], instance=instance)
                else:
                    message = (
                        f"Missing section in config file,"
                        f' default values are "{name}": {kw_defaults_json}'
                    )
                    output = ValidationOutput(
                        validation=validation_class.validation,
                        result=ValidationResult.ERROR,
                        enforcement=validation_class.enforcement,
                        config=None,
                        message=message,
                    )
            else:
                output = validation.validate(instance=instance)
        except Exception as e:
            kw_error = f"Error loading parameters of {name} from config file"
            kw_verbose = f"Default parameters are {kw_defaults_json}"
            error_message = "Unable to validate due to unsupported environment"
            output = ValidationOutput(
                validation=validation_class.validation,
                result=ValidationResult.ERROR,
                enforcement=validation_class.enforcement,
                config=None,
                message=kw_error if isinstance(e, TypeError) else error_message,
                verbose_message=kw_verbose if isinstance(e, TypeError) else str(e),
            )
            exit_code = 1
        validation_outputs.append(output)

    validation_outputs.sort(key=lambda x: x.result)
    final_result = get_final_result(validation_outputs)

    if args.log:

        outfile_name = (
            f"logs/{datetime.datetime.utcnow().replace(microsecond=0).isoformat()}"
            "Z_WIGValidationLog.json"
        )

        if not os.path.isdir("logs"):
            try:
                os.mkdir("logs")
            except OSError:
                if not args.quiet:
                    print(
                        "Failed to create logs folder,"
                        "producing log file in current directory"
                    )
                outfile_name = outfile_name.split("/")[1]

        with open(outfile_name, "w", encoding="utf-8") as outfile:
            json.dump(
                sanitize_json(final_result), outfile, ensure_ascii=False, indent=2
            )

    table_headers = map(
        lambda x: Colors.BOLD + x + Colors.ENDC,
        ["Validation", "Result", "Enforcement", "Configuration", "Message"],
    )
    table = PrettyTable(table_headers)
    table.align[Colors.BOLD + "Message" + Colors.ENDC] = "l"
    table.hrules = ALL

    for output in validation_outputs:
        result = COLOR_MAP[output.result] + output.result + Colors.ENDC
        total_message = output.message
        if args.verbose and (output.verbose_message is not None):
            total_message += f"...\n{output.verbose_message}"
        table.add_row(
            [
                output.validation,
                result,
                output.enforcement,
                output.config,
                total_message,
            ]
        )

    if not args.quiet:
        print(table)
        print("\n")
        print(
            f"{final_result.pass_count}/{final_result.total_count}"
            " Validations Passed"
        )
        print(final_result)
        if args.log:
            print(f"Log file produced: {outfile_name}")
        print("\n")
    return exit_code


if __name__ == "__main__":
    if os.geteuid() != 0:
        print(
            "You need to have root privileges to run this script.",
            "Please try again, this time using 'sudo'. Exiting."
        )
        exit_code = 1
    else:
        exit_code = main()
    sys.exit(exit_code)
