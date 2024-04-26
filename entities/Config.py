class Config:
    api_token = None

    first_profile = 0
    profiles_number = 0

    metamask_file = ''

    thread_number = ''

    tag_name = ''

    metamask_password = ''

    def __init__(self, api_token, first_profile, profiles_number, metamask_file, thread_number, tag_name, driver_version, metamask_password):
        self.api_token = api_token
        self.first_profile = int(first_profile)
        self.profiles_number = int(profiles_number)
        self.metamask_file = metamask_file
        self.thread_number = int(thread_number)
        self.tag_name = tag_name
        self.metamask_password = metamask_password
        self.driver_version = driver_version
