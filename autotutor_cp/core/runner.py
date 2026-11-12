"""POSIX resource launcher, avoiding preexec_fn in Streamlit's threads."""
import math
import os
import sys

if __name__ == '__main__':
    import resource
    seconds, memory, output, executable, *arguments = sys.argv[1:]
    resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(float(seconds)) + 1,) * 2)
    resource.setrlimit(resource.RLIMIT_AS, (int(memory) * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (int(output),) * 2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    os.execv(executable, [executable, *arguments])
