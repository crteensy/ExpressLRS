import serial, time, sys
import subprocess
import argparse
import serials_find

def dbg_print(line=''):
    sys.stdout.write(line + '\n')
    sys.stdout.flush()

try:
    import pexpect.fdpexpect
except ImportError:
    sys.stdout.write("Installing pexpect")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pexpect"])
    try:
        import pexpect.fdpexpect
    except ImportError:
        env.Execute("$PYTHONEXE -m pip install pexpect")
        try:
            import pexpect.fdpexpect
        except ImportError:
            pexpect = None

def etx_passthrough_init(port, requestedBaudrate):
    sys.stdout.flush()
    dbg_print("======== PASSTHROUGH INIT ========")
    dbg_print("  Trying to initialize %s @ %s" % (port, requestedBaudrate))

    s = serial.Serial(port=port, baudrate=115200,
        bytesize=8, parity='N', stopbits=1,
        timeout=1, xonxoff=0, rtscts=0)

    rl = pexpect.fdpexpect.fdspawn(s, timeout=1)

    rl.sendline("set pulses 0")
    rl.expect("set: ")
    rl.expect("> ")
    rl.sendline("set rfmod 0 power off")
    rl.expect("set: ")
    rl.expect("> ")
    time.sleep(.5)
    rl.sendline("set rfmod 0 bootpin 1")
    rl.expect("set: ")
    rl.expect("> ")
    time.sleep(.1)
    rl.sendline("set rfmod 0 power on")
    rl.expect("set: ")
    rl.expect("> ")
    time.sleep(.1)
    rl.sendline("set rfmod 0 bootpin 0")
    rl.expect("set: ")
    rl.expect("> ")

    cmd = "serialpassthrough rfmod 0 %s" % requestedBaudrate

    dbg_print("Enabling serial passthrough...")
    dbg_print("  CMD: '%s'" % cmd)
    rl.sendline(cmd)
    time.sleep(.2)
    rl.close()
    dbg_print("======== PASSTHROUGH DONE ========")

def init_passthrough(source, target, env):
    env.AutodetectUploadPort([env])
    port = env['UPLOAD_PORT']
    etx_passthrough_init(port, env['UPLOAD_SPEED'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Initialize EdgeTX passthrough to internal module")
    parser.add_argument("-b", "--baud", type=int, default=460800,
        help="Baud rate for passthrough communication")
    parser.add_argument("-p", "--port", type=str,
        help="Override serial port autodetection and use PORT")
    args = parser.parse_args()

    if (args.port == None):
        args.port = serials_find.get_serial_port()

    etx_passthrough_init(args.port, args.baud)
