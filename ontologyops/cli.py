"""Command-line interface for OntologyOps."""

import argparse
import sys
from pathlib import Path


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ontologyops",
        description="Ontology version control, testing, and deployment",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # version
    subparsers.add_parser("version", help="Show version")

    # snapshot
    snap_parser = subparsers.add_parser("snapshot", help="Create version snapshot")
    snap_parser.add_argument("ontology", help="Path to ontology file")
    snap_parser.add_argument("--author", required=True, help="Author")
    snap_parser.add_argument("--message", required=True, help="Commit message")

    # test
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("ontology", help="Path to ontology file")

    # deploy
    deploy_parser = subparsers.add_parser("deploy", help="Deploy ontology")
    deploy_parser.add_argument("ontology", help="Path to ontology file")
    deploy_parser.add_argument("--url", default="http://localhost:7200", help="Triple store URL")

    args = parser.parse_args()

    if args.command == "version":
        from ontologyops import __version__
        print(__version__)
        return 0

    if args.command == "snapshot":
        from ontologyops import OntologyVersionControl
        vc = OntologyVersionControl(args.ontology)
        h = vc.create_snapshot(author=args.author, message=args.message)
        print(f"Created snapshot: {h}")
        return 0

    if args.command == "test":
        from ontologyops import OntologyTestSuite
        suite = OntologyTestSuite(args.ontology)
        report = suite.run_all_tests()
        print(f"Tests: {report.passed_tests}/{report.total_tests} passed")
        if not report.passed:
            print("Failed:", report.failed_tests)
            return 1
        return 0

    if args.command == "deploy":
        from ontologyops import OntologyDeployer
        deployer = OntologyDeployer(triple_store_url=args.url)
        result = deployer.deploy(args.ontology)
        if result["success"]:
            print("Deployment successful")
            return 0
        print("Deployment failed:", result.get("error", "unknown"))
        return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
