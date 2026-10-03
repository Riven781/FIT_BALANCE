class DomainError(Exception):
  pass

class CategoryDoesNotBelongToHierarchy(DomainError):
  pass

class CategoryAssignmentTaskBelongsToAnotherUser(DomainError): #tasks
  pass

class CategoryAssignmentTaskNotAllowed(DomainError): #tasks
  pass

class CategoryAssignmentTasksRequirePlannedHierarchy(DomainError):
  pass

class UserIdRequired(DomainError): #task
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

class IssueCanNotBeReset(DomainError):
  pass


class IssueCanNotBeMarkedAsObsolete(DomainError):
  pass

class ProductCategoryAssignmentConflict(DomainError):
  pass


class ProductVersionConflict(DomainError):
  pass

class FieldDoesNotExistInReportItems(DomainError):
  pass