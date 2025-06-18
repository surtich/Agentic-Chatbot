from configparser import ConfigParser

class Config:
    def __init__(self,config_file="./src/langgraphagenticai/ui/uiconfigfile.ini"):
        self.config=ConfigParser()
        self.config.read(config_file)

    def get_llm_options(self):
        return self.config["DEFAULT"].get("LLM_OPTIONS", "Opción LLM no configurada").split(", ")

    def get_usecase_options(self):
        return self.config["DEFAULT"].get("USECASE_OPTIONS", "Caso de uso no configurado").split(", ")

    def get_model_options(self, provider):
        section = provider.strip()
        if section in self.config:
            return self.config[section].get("MODEL_OPTIONS", "Modelo no configurado").split(", ")
        return ["Modelo no configurado"]
    
    def get_base_url(self, provider):
        section = provider.strip()
        if section in self.config:
            return self.config[section].get("BASE_URL")

    def get_page_title(self):
        return self.config["DEFAULT"].get("PAGE_TITLE", "Título no configurado")

