class FullnessMixin:
    class FullnessMode:
        SHORT = 'short'
        FULL = 'full'

        __default__ = FULL

    def fullness(self):
        params = self.request.query_params
        if 'short' in params:
            return self.FullnessMode.SHORT
        if 'full' in params:
            return self.FullnessMode.FULL
        else:
            return self.FullnessMode.__default__
