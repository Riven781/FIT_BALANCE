from fastapi import Request
from fastapi.responses import JSONResponse

from product_catalog_context.domain.errors import CategoryAssignmentTasksRequirePlannedHierarchy, CategoryDoesNotBelongToHierarchy, CategoryHierarchyCannotBeEdited, CategoryHierarchyCannotBePublished, CategoryHierarchyCannotBeRevertedToDraft, CategoryHierarchyIsNotDraft, DraftCategoryHierarchyCannotBeCreated, DraftCategoryHierarchyCannotBeDeleted
from product_catalog_context.infrastructure.aiosqlite_repository.errors.errors import RepositoryError
from product_catalog_context.application.errors.errors import CategoryAssignmentRequiresProductEditor, CategoryDoesNotBelongToActiveHierarchy, CategoryHierarchyDoesNotExist, DraftCategoryHierarchyExists, InvalidProductCategoryId, InvalidProductDataError, ProductAlreadyExistsError, ProductNotFoundError, ProductReportExistsForThisVersion, TaskDoesNotExist, TaskNotFoundError

def register_exception_handlers(app):
  app.add_exception_handler(RepositoryError, repository_error_handler)
  app.add_exception_handler(ProductNotFoundError, product_not_found_handler)
  app.add_exception_handler(InvalidProductDataError, invalid_product_data_handler)
  app.add_exception_handler(InvalidProductCategoryId, invalid_product_category_id_handler)
  app.add_exception_handler(ProductAlreadyExistsError, product_already_exists_handler)
  app.add_exception_handler(CategoryDoesNotBelongToActiveHierarchy, category_does_not_belong_to_active_hierarchy_handler)
  app.add_exception_handler(CategoryHierarchyDoesNotExist, category_hierarchy_not_found_handler)
  app.add_exception_handler(CategoryHierarchyCannotBeEdited, category_hierarchy_cannot_be_edited_handler)
  app.add_exception_handler(CategoryHierarchyCannotBePublished, category_hierarchy_cannot_be_published)
  app.add_exception_handler(CategoryHierarchyIsNotDraft, category_hierarchy_cannot_be_planned_for_publication)
  app.add_exception_handler(DraftCategoryHierarchyCannotBeCreated, draft_category_cannot_be_created)
  app.add_exception_handler(DraftCategoryHierarchyExists, draft_hierarchy_exists)
  app.add_exception_handler(DraftCategoryHierarchyCannotBeDeleted, category_hierarchy_cannot_be_deleted_handler)
  app.add_exception_handler(CategoryHierarchyCannotBeRevertedToDraft, category_hierarchy_cannot_be_reverted_to_draft_handler)
  app.add_exception_handler(TaskDoesNotExist, task_does_not_exists)
  app.add_exception_handler(TaskNotFoundError, task_does_not_exists)
  app.add_exception_handler(CategoryAssignmentTasksRequirePlannedHierarchy, category_assignment_task_not_allowed_handler)
  app.add_exception_handler(CategoryDoesNotBelongToHierarchy, category_does_not_belong_to_hierarchy_handler)
  app.add_exception_handler(CategoryAssignmentRequiresProductEditor, category_assignment_requires_product_editor_handler)
  app.add_exception_handler(ProductReportExistsForThisVersion, product_report_exists_for_this_product_version)




async def repository_error_handler(request: Request, exc: RepositoryError):
  return JSONResponse(
    status_code=500,
    content={
      "message": 'Internal Server Error'
    }
  )

async def product_not_found_handler(req, exc):
  return JSONResponse(
    status_code=404,
    content={
      "message": "Not Found"
    }
  )


async def category_does_not_belong_to_active_hierarchy_handler(req, exc):
  return JSONResponse(
    status_code=422,
    content={
      "message": "Category does not belong to the active hierarchy"
    }
  )

async def invalid_product_data_handler(req, exc):
  return JSONResponse(
    status_code=400,
    content={
      "message": "Bad Request"
    }
  )

async def invalid_product_category_id_handler(req, exc):
  return JSONResponse(
    status_code=404,
    content={
      "message": "Product category doesn't exist."
    }
  )

async def product_already_exists_handler(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": "Conflict"
    }
  )


async def category_hierarchy_not_found_handler(req, exc):
  return JSONResponse(
    status_code=404,
    content={
      "message": "Category hierarchy category doesn't exist.",
    }
  )


async def category_hierarchy_cannot_be_edited_handler(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": "Only draft can be edited."
    }
  )


async def category_hierarchy_cannot_be_published(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": "Only planned for publication can be published.",
    }
  )





async def category_hierarchy_cannot_be_planned_for_publication(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": "Only draft can be planned for publication."
    }
  )

async def draft_category_cannot_be_created(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": "Draft only can be created based on active category."
    }
  )

async def draft_hierarchy_exists(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": "Draft hierarchy already exists."
    }
  )



async def category_hierarchy_cannot_be_deleted_handler(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": "Only draft category can be deleted."
    }
  )

async def category_hierarchy_cannot_be_reverted_to_draft_handler(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": "Only planned for publication hierarchy can be reverted to draft."
    }
  )

async def task_does_not_exists(req, exc):
  return JSONResponse(
    status_code=404,
    content={
      "message": "Task does not exist."
    }
  )

def category_assignment_task_not_allowed_handler(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": 'Hierarchy must be planned for publication.'
    }
  )

def category_does_not_belong_to_hierarchy_handler(req, exc):
  return JSONResponse(
    status_code=422,
    content={
      "message": 'Category does not belong to hierarchy.'
    }
  )

def category_assignment_requires_product_editor_handler(req, exc):
  return JSONResponse(
    status_code=422,
    content={
      "message": 'Category assignment requires product editor.'
    }
  )

def product_report_exists_for_this_product_version(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": 'You have already created a report for this product version.'
    }
  )