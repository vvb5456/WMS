import logging
import os
import subprocess
import threading
import time

logger = logging.getLogger(__name__)


def _is_enabled() -> bool:
    return os.getenv("GPIO_ENABLED", "false").lower() in ("1", "true", "yes")


def _config() -> dict:
    return {
        "chip": os.getenv("GPIO_CHIP", "gpiochip1"),
        "line": int(os.getenv("GPIO_LINE", "73")),
        "seconds": float(os.getenv("GPIO_PULSE_SECONDS", "5")),
    }


def pulse_on_approve() -> bool:
    """Orange Pi 物理引脚 7 (PC9) 输出高电平，默认持续 5 秒。异步执行，不阻塞审核接口。"""
    if not _is_enabled():
        return False
    cfg = _config()
    threading.Thread(target=_pulse_worker, args=(cfg,), daemon=True).start()
    return True


def approve_message(base: str = "审核通过") -> str:
    if not _is_enabled():
        return base
    secs = _config()["seconds"]
    return f"{base}，物理引脚7已输出高电平{secs:g}秒"


def _pulse_worker(cfg: dict) -> None:
    chip, line, seconds = cfg["chip"], cfg["line"], cfg["seconds"]
    try:
        _pulse_via_gpioset(chip, line, seconds)
        logger.info("GPIO pulse ok: %s line %s high %.1fs", chip, line, seconds)
    except Exception as e1:
        try:
            _pulse_via_gpiod(chip, line, seconds)
            logger.info("GPIO pulse ok (gpiod): %s line %s high %.1fs", chip, line, seconds)
        except Exception as e2:
            logger.error("GPIO pulse failed: gpioset=%s gpiod=%s", e1, e2)


def _pulse_via_gpioset(chip: str, line: int, seconds: float) -> None:
    cmds = [
        ["gpioset", "--mode=time", f"--sec={seconds}", chip, f"{line}=1"],
        ["gpioset", "-c", chip, f"{line}=1", "-m", "time", "-s", str(seconds)],
    ]
    last_err = None
    for cmd in cmds:
        try:
            subprocess.run(cmd, check=True, timeout=seconds + 5)
            return
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            last_err = e
    raise RuntimeError(f"gpioset failed: {last_err}")


def _pulse_via_gpiod(chip: str, line: int, seconds: float) -> None:
    import gpiod

    with gpiod.Chip(chip) as gchip:
        req = gchip.get_line(line)
        req.request(consumer="wms", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
        try:
            req.set_value(1)
            time.sleep(seconds)
            req.set_value(0)
        finally:
            req.release()
