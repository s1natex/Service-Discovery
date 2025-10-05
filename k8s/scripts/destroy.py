#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time

K8S_NS = "app"  # fixed: was "service-discovery"
INGRESS_NS = "ingress-nginx"
ARGO_NS = "argocd"
INGRESS_MANIFEST = "https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml"

def run(cmd: list[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, text=True, capture_output=capture_output)

def kubectl(*args: str, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    return run(["kubectl", *args], check=check, capture_output=capture_output)

def ns_exists(ns: str) -> bool:
    res = kubectl("get", "ns", ns, check=False, capture_output=True)
    return res.returncode == 0

def wait_for_ns_gone(ns: str, timeout_sec: int = 300) -> None:
    print(f"Waiting for namespace {ns} to terminate (timeout {timeout_sec}s)...")
    start = time.time()
    while time.time() - start < timeout_sec:
        if not ns_exists(ns):
            print(f"Namespace {ns} deleted.")
            return
        time.sleep(2)
    raise SystemExit(f"Timeout: namespace {ns} still exists after {timeout_sec}s")

def main() -> None:
    parser = argparse.ArgumentParser(description="Destroy stack from Docker Desktop K8s")
    parser.add_argument("--context", default="docker-desktop", help="kubectl context (default: docker-desktop)")
    parser.add_argument("--remove-ingress", action="store_true", help="Also remove ingress-nginx controller")
    parser.add_argument("--remove-argocd", action="store_true", help="Also remove Argo CD (argocd namespace)")
    parser.add_argument("--wait-timeout", type=int, default=300, help="Timeout in seconds for waits (default 300)")
    args = parser.parse_args()

    print(f"Setting kubectl context to {args.context} ...")
    kubectl("config", "use-context", args.context)

    if ns_exists(K8S_NS):
        print(f"Deleting namespace {K8S_NS} ...")
        kubectl("delete", "ns", K8S_NS)
        wait_for_ns_gone(K8S_NS, timeout_sec=args.wait_timeout)
    else:
        print(f"Namespace {K8S_NS} not found; skipping.")

    if args.remove_argocd:
        if ns_exists(ARGO_NS):
            print(f"Deleting namespace {ARGO_NS} ...")
            kubectl("delete", "ns", ARGO_NS)
            wait_for_ns_gone(ARGO_NS, timeout_sec=args.wait_timeout)
        else:
            print(f"Namespace {ARGO_NS} not found; skipping Argo CD removal.")

    if args.remove_ingress:
        if ns_exists(INGRESS_NS):
            print("Deleting ingress-nginx controller (this may take a while) ...")
            kubectl("delete", "-f", INGRESS_MANIFEST, check=False)
            if ns_exists(INGRESS_NS):
                print("Namespace still present; attempting namespace delete ...")
                kubectl("delete", "ns", INGRESS_NS, check=False)
                wait_for_ns_gone(INGRESS_NS, timeout_sec=args.wait_timeout)
        else:
            print("ingress-nginx not found; skipping removal.")

    print("\nCleanup complete.")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\nCommand failed: {' '.join(e.cmd)}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        sys.exit(e.returncode)
