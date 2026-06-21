from data_generator import generate_dataset
from evals import run_eval_benchmark


class SafeRedTeamAgent:
    """
    Autonomous evaluation agent for synthetic biosecurity screening tests.

    Workflow:
    Generate synthetic dataset
    -> Run evaluation benchmark
    -> Collect metrics
    -> Rank results
    -> Generate markdown report
    """

    def __init__(self, data_dir="data", seeds=range(10)):
        self.data_dir = data_dir
        self.seeds = list(seeds)
        self.results = []

    def run(self):
        print("Starting Safe Red-Team Agent")

        for seed in self.seeds:
            print(f"\nRunning evaluation cycle: seed={seed}")

            generate_dataset(output_dir=self.data_dir, seed=seed)

            report = run_eval_benchmark(data_dir=self.data_dir)

            self.results.append({
                "seed": seed,
                "summary": report["summary"]
            })

        return self.results

    def rank_results(self):
        leaderboard = []

        for result in self.results:
            summary = result["summary"]

            leaderboard.append({
                "seed": result["seed"],
                "baseline_detection": summary["threat_baseline"]["detection_rate"],
                "codon_opt_detection": summary["threat_codon_opt"]["detection_rate"],
                "split_detection": summary["threat_split"]["detection_rate"],
                "chimeric_detection": summary["threat_chimeric"]["detection_rate"],
                "benign_false_positive": summary["benign_baseline"]["false_positive_rate"]
            })

        leaderboard.sort(key=lambda x: x["baseline_detection"], reverse=True)
        return leaderboard

    def print_leaderboard(self):
        leaderboard = self.rank_results()

        print("\n=== Safe Red-Team Leaderboard ===")

        for idx, row in enumerate(leaderboard, start=1):
            print(
                f"{idx}. Seed={row['seed']} | "
                f"Baseline={row['baseline_detection']:.2%} | "
                f"CodonOpt={row['codon_opt_detection']:.2%} | "
                f"Split={row['split_detection']:.2%} | "
                f"Chimeric={row['chimeric_detection']:.2%} | "
                f"FalsePositive={row['benign_false_positive']:.2%}"
            )

    def generate_markdown_report(self, output_file="agent_report.md"):
        leaderboard = self.rank_results()

        with open(output_file, "w") as f:
            f.write("# BioGuard Red Team Agent Report\n\n")

            f.write("## Overview\n")
            f.write(
                "This report summarizes repeated synthetic biosecurity screening "
                "evaluations across safe toy-sequence datasets.\n\n"
            )

            f.write("## Leaderboard\n\n")
            f.write(
                "| Rank | Seed | Baseline Detection | Codon-Opt Detection | "
                "Split Detection | Chimeric Detection | Benign False Positive |\n"
            )
            f.write(
                "|---|---:|---:|---:|---:|---:|---:|\n"
            )

            for idx, row in enumerate(leaderboard, start=1):
                f.write(
                    f"| {idx} | {row['seed']} | "
                    f"{row['baseline_detection']:.2%} | "
                    f"{row['codon_opt_detection']:.2%} | "
                    f"{row['split_detection']:.2%} | "
                    f"{row['chimeric_detection']:.2%} | "
                    f"{row['benign_false_positive']:.2%} |\n"
                )

            f.write("\n## Safety Boundary\n")
            f.write(
                "This agent uses synthetic toy sequences and controlled evaluation "
                "scenarios only. It is designed to evaluate screening robustness, "
                "not to optimize biological function or enable real-world misuse.\n"
            )

        print(f"\nReport written to {output_file}")


if __name__ == "__main__":
    agent = SafeRedTeamAgent(seeds=range(10))

    agent.run()
    agent.print_leaderboard()
    agent.generate_markdown_report()

    print("\nSafe Red-Team Agent completed.")