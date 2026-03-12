import subprocess
import os

import decky_plugin

class Plugin:
    async def _main(self):
        self.performance_enabled = False
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        decky_plugin.logger.info("OneXFly Performance Plugin загружен")

    async def toggle_performance(self, enable: bool):
        """Включение/отключение performance режима"""
        try:
            if enable:
                # Отключаем power-profiles-daemon
                subprocess.run(["sudo", "systemctl", "stop", "power-profiles-daemon"], 
                             capture_output=True)
                subprocess.run(["sudo", "systemctl", "disable", "power-profiles-daemon"], 
                             capture_output=True)
                
                # Устанавливаем CPU governor
                for cpu in range(0, 16):  # OneXFly имеет 16 потоков
                    gov_path = f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor"
                    if os.path.exists(gov_path):
                        subprocess.run(["sudo", "tee", gov_path], 
                                     input=b"performance", capture_output=True)
                
                # GPU performance режим
                subprocess.run(["sudo", "tee", "/sys/class/drm/card0/device/power_dpm_force_performance_level"], 
                             input=b"manual", capture_output=True)
                subprocess.run(["sudo", "tee", "/sys/class/drm/card0/device/pp_power_profile_mode"], 
                             input=b"1", capture_output=True)
                
                self.performance_enabled = True
                decky_plugin.logger.info("Performance режим включен")
                return "Performance режим включен"
            else:
                # Возвращаем стандартные настройки
                for cpu in range(0, 16):
                    gov_path = f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor"
                    if os.path.exists(gov_path):
                        subprocess.run(["sudo", "tee", gov_path], 
                                     input=b"schedutil", capture_output=True)
                
                subprocess.run(["sudo", "tee", "/sys/class/drm/card0/device/power_dpm_force_performance_level"], 
                             input=b"auto", capture_output=True)
                
                # Включаем power-profiles-daemon обратно
                subprocess.run(["sudo", "systemctl", "enable", "power-profiles-daemon"], 
                             capture_output=True)
                subprocess.run(["sudo", "systemctl", "start", "power-profiles-daemon"], 
                             capture_output=True)
                
                self.performance_enabled = False
                decky_plugin.logger.info("Performance режим отключен")
                return "Performance режим отключен"
                
        except Exception as e:
            decky_plugin.logger.error(f"Ошибка: {str(e)}")
            return f"Ошибка: {str(e)}"

    async def get_status(self):
        """Получение текущего статуса"""
        return {
            "enabled": self.performance_enabled
        }

    async def _unload(self):
        decky_plugin.logger.info("OneXFly Performance Plugin выгружен")

    async def _migration(self):
        decky_plugin.logger.info("Миграция плагина")
