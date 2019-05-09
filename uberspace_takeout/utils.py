import subprocess


def run_command(cmd, input_text=None):
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
    )
    out, _ = p.communicate(input_text)
    return [l for l in out.split('\n') if l]


def run_uberspace(*cmd):
    return run_command(['uberspace'] + list(cmd))
