#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time
from pathlib import Path

K8S_NS = "service-discovery"
INGRESS_NS = "ingress-nginx"
INGRESS_MANIFEST = "https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml"

MANIFESTS = [
    "consul.yaml",
    "service-a.yaml",
    "service-b.yaml",
    "service-c.yaml",
    "service-d.yaml",
    "healthz.yaml",
    "gateway.yaml",
    "frontend.yaml",
]

def run(cmd: list[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, text=True, capture_output=capture_output)

def kubectl(*args: str, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    return run(["kubectl", *args], check=check, capture_output=capture_output)

def ns_exists(ns: str) -> bool:
    res = kubectl("get", "ns", ns, check=False, capture_output=True)
    return res.returncode == 0

def wait_for_deploy(ns: str, name: str, timeout_sec: int = 300) -> None:
    print(f"Waiting for Deployment {name} in {ns} to become ready (timeout {timeout_sec}s)...")
    kubectl("-n", ns, "rollout", "status", f"deploy/{name}", f"--timeout={timeout_sec}s")

def wait_for_pods_ready(ns: str, label_selector: str = "", timeout_sec: int = 300) -> None:
    print(f"Waiting for Pods in {ns} to be Ready (timeout {timeout_sec}s)...")
    start = time.time()
    while time.time() - start < timeout_sec:
        args = ["-n", ns, "get", "pods", "--no-headers"]
        if label_selector:
            args.extend(["-l", label_selector])
        res = kubectl(*args, check=False, capture_output=True)
        if res.returncode == 0 and res.stdout.strip():
            lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
            ready = 0
            total = 0
            for ln in lines:
                cols = ln.split()
                if len(cols) >= 2:
                    total += 1
                    ready_col = cols[1]
                    try:
                        cur, want = ready_col.split("/")
                        if int(cur) == int(want):
                            ready += 1
                    except Exception:
                        pass
            if total > 0 and ready == total:
                print(f"All Pods Ready in {ns}.")
                return
        time.sleep(2)
    raise SystemExit(f"Timeout: Pods in namespace {ns} not Ready in {timeout_sec}s")

def apply_file(path: Path, namespace: str | None = None) -> None:
    if namespace:
        kubectl("-n", namespace, "apply", "-f", str(path))
    else:
        kubectl("apply", "-f", str(path))

def apply_many(files: list[Path], namespace: str) -> None:
    for f in files:
        print(f"Applying {f.name} ...")
        apply_file(f, namespace)

def ensure_ingress_nginx(install: bool, wait_timeout: int) -> None:
    if ns_exists(INGRESS_NS):
        print("ingress-nginx already present; skipping install.")
    else:
        if not install:
            print("ingress-nginx namespace not found and --install-ingress was not set.")
            print("Either install it first or re-run with --install-ingress.")
            raise SystemExit(1)
        print("Installing ingress-nginx controller ...")
        kubectl("apply", "-f", INGRESS_MANIFEST)
        try:
            wait_for_deploy(INGRESS_NS, "ingress-nginx-controller", timeout_sec=wait_timeout)
        except subprocess.CalledProcessError:
            wait_for_pods_ready(INGRESS_NS, timeout_sec=wait_timeout)

def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy Service Discovery stack to Docker Desktop K8s")
    parser.add_argument("--context", default="docker-desktop", help="kubectl context (default: docker-desktop)")
    parser.add_argument("--install-ingress", action="store_true", help="Install ingress-nginx if missing")
    parser.add_argument("--wait-timeout", type=int, default=300, help="Timeout in seconds for waits (default 300)")
    args = parser.parse_args()

    scripts_dir = Path(__file__).resolve().parent
    k8s_dir = scripts_dir.parent
    ns_file = k8s_dir / "namespace.yaml"
    ingress_file = k8s_dir / "ingress.yaml"
    manifest_paths = [k8s_dir / f for f in MANIFESTS]

    print(f"Setting kubectl context to {args.context} ...")
    kubectl("config", "use-context", args.context)

    print(f"Applying namespace: {ns_file}")
    apply_file(ns_file)

    print("Applying core manifests to namespace 'service-discovery' ...")
    apply_many(manifest_paths, K8S_NS)

    wait_for_pods_ready(K8S_NS, timeout_sec=args.wait_timeout)

    ensure_ingress_nginx(install=args.install_ingress, wait_timeout=args.wait_timeout)

    print(f"Applying ingress: {ingress_file.name}")
    time.sleep(30)  # Give ingress-nginx a moment to settle
    apply_file(ingress_file, K8S_NS)

    print("\nDeployment complete.\n")
    print("Quick checks:")
    print(f"  kubectl get pods -n {K8S_NS}")
    print(f"  kubectl get svc  -n {K8S_NS}")
    print(f"  curl http://localhost/            # frontend")
    print(f"  curl http://localhost/services    # gateway services")
    print(f"  curl http://localhost/healthz     # gateway health")

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
