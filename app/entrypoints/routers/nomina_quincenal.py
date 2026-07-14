from fastapi import APIRouter, Depends, status
from typing import List


from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import NominaQuincenalCreate, NominaQuincenalRead, NominaQuincenalUpdate
from app.service_layer import services