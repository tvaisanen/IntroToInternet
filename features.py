import self as self


class Features:

    def __init__(self):
        self.multipart_status = False
        self.confidentiality_status = False
        self.integrity_status = False
        self.availability_status = False

    def set_multipart_status(self, status):
        self.multipart_status = status


    def get_multipart_status(self):
        """
        :return: (boolean, flag) flag=None if false
        """
        if self.multipart_status:
            return self.multipart_status, 'M'
        else:
            return self.multipart_status, None


    def set_confidentiality_status(self, status):
        self.confidentiality_status = status


    def get_confidentiality_status(self):
        """
        :return: (boolean, flag) flag=None if false
        """
        if self.confidentiality_status:
            return self.confidentiality_status, 'C'
        else:
            return self.confidentiality_status, None


    def set_integrity_status(self, status):
        self.integrity_status = status


    def get_integrity_status(self):
        """
        :return: (boolean, flag) flag=None if false
        """
        if self.integrity_status:
            return self.integrity_status, 'I'
        else:
            return self.integrity_status, None


    def set_availability_status(self, status):
        self.availability_status = status


    def get_availability_status(self):
        """
        :return: (boolean, flag) flag=None if false
        """
        if self.availability_status:
            return self.availability_status, 'A'
        else:
            return self.availability_status, None