class DomainError(Exception):
  pass

class CategoryHierarchyIsNotDraft(DomainError):
  pass

class OnlyDraftHierarchyCanBeUpdated(DomainError):
  pass

class DraftCategoryHierarchyCannotBeCreated(DomainError):
  pass

class DraftCategoryCannotBeCreated(DomainError):
  pass

class DraftCategoryIdCountMismatch(DomainError):
  pass

class CategoryHierarchyCannotBePublished(DomainError):
  pass

class CategoryHierarchyCannotBeRevertedToDraft(DomainError):
  pass

class ParentCategoryNotInHierarchy(DomainError):
  pass

class DraftCategoryHierarchyCannotBeDeleted(DomainError):
  pass

class CategoryAssignmentNotAllowed(DomainError):
  pass

class CategoryHierarchyCannotBeEdited(DomainError):
  pass

#tasks
class TaskCannotBeCompleted(DomainError):
  pass

class TaskCannotBeCancelled(DomainError):
  pass

class IssueCanNotBeConfirmed(DomainError):
  pass

class IssueCanNotBeRejected(DomainError):
  pass

class IssueCanNotBeMarkedAsObsolete(DomainError):
  pass