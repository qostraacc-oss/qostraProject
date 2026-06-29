class WorkspaceResourceMixin:
    @property
    def project_context(self):
        """
        Returns the parent Project instance for the resource.
        Must be implemented by each model.
        """
        raise NotImplementedError("Models using WorkspaceResourceMixin must implement project_context.")
