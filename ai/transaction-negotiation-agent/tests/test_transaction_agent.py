import os

# db.py requires this variable during import.
# Unit tests mock persistence, so no real DB connection is made.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://test:test@localhost:5432/test"
)

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    StartWorkflowRequest,
    ApprovalDecisionRequest,
    ApprovalStatus,
    TargetType,
    WorkflowStatus,
)

from app.tools.registry import (
    build_registry,
    ToolInput,
    CounterOfferInput,
    execute_counter_offer,
)

from app.agents import workflow


# ---------------------------------------------------------
# Request/schema validation
# ---------------------------------------------------------

def test_valid_workflow_request():
    req = StartWorkflowRequest(
        objective="Negotiate a purchase counter-offer",
        target_type=TargetType.PURCHASE_OFFER,
        target_id=10,
    )

    assert req.target_id == 10
    assert req.target_type == TargetType.PURCHASE_OFFER


def test_target_id_must_be_positive():
    with pytest.raises(ValidationError):
        StartWorkflowRequest(
            objective="Negotiate offer",
            target_type=TargetType.PURCHASE_OFFER,
            target_id=0,
        )


# ---------------------------------------------------------
# Tool allow-list
# ---------------------------------------------------------

def test_unknown_tool_is_rejected():
    registry = build_registry()

    result = registry.execute(
        "delete_transaction",
        "ActionAgent",
        {
            "target_type": "PurchaseOffer",
            "target_id": 10,
            "objective": "Delete the transaction",
        },
        authorization="Bearer test",
    )

    assert result.succeeded is False
    assert result.error == "Tool is not allow-listed."


def test_agent_cannot_use_unauthorized_tool():
    registry = build_registry()

    result = registry.execute(
        "prepare_counter_offer",
        "DomainAnalysisAgent",
        {
            "target_type": "PurchaseOffer",
            "target_id": 10,
            "objective": "Prepare counter offer",
        },
        authorization="Bearer test",
    )

    assert result.succeeded is False
    assert result.error == "Agent is not authorized for this tool."


# ---------------------------------------------------------
# Human approval marker
# ---------------------------------------------------------

def test_prepare_counter_offer_requires_human_approval():
    registry = build_registry()

    result = registry.execute(
        "prepare_counter_offer",
        "ActionAgent",
        {
            "target_type": "PurchaseOffer",
            "target_id": 10,
            "objective": "Prepare counter offer",
        },
        authorization="Bearer test",
    )

    assert result.succeeded is True
    assert result.data["action"] == "PREPARE_COUNTER_OFFER"
    assert result.data["requires_human_approval"] is True


# ---------------------------------------------------------
# Full workflow must stop before high-impact execution
# ---------------------------------------------------------

def test_workflow_stops_at_human_approval(monkeypatch):
    monkeypatch.setattr(
        workflow,
        "persist",
        lambda w: None,
    )

    plan = workflow.WorkflowPlan(
        objective="Negotiate purchase offer",
        steps=[
            workflow.PlanStep(
                sequence=1,
                agent_role="PlannerAgent",
                responsibility="Plan workflow",
                input_contract="workflow request",
                output_contract="plan",
            ),
            workflow.PlanStep(
                sequence=2,
                agent_role="DomainAnalysisAgent",
                responsibility="Analyze transaction",
                input_contract="transaction",
                output_contract="analysis",
            ),
            workflow.PlanStep(
                sequence=3,
                agent_role="ActionAgent",
                responsibility="Prepare action",
                input_contract="analysis",
                output_contract="proposal",
            ),
            workflow.PlanStep(
                sequence=4,
                agent_role="ValidationAgent",
                responsibility="Validate action",
                input_contract="proposal",
                output_contract="validation",
            ),
        ],
    )

    monkeypatch.setattr(
        workflow,
        "plan_workflow",
        lambda *args, **kwargs: plan,
    )

    def fake_structured_output(
        agent_role,
        objective,
        evidence,
        instruction,
    ):
        if agent_role == "ActionAgent":
            return {
                "action_payload": {
                    "offerAmount": 25000000,
                    "conditions": "Subject to inspection",
                },
                "reason": "Counter-offer based on supplied evidence",
                "required_approval": True,
            }

        return {
            "analysis": "Transaction evidence reviewed"
        }

    monkeypatch.setattr(
        workflow,
        "structured_agent_output",
        fake_structured_output,
    )

    executed_tools = []

    def fake_registry_execute(
        name,
        agent_role,
        payload,
        authorization=None,
    ):
        executed_tools.append(name)

        return workflow.registry._tools[name][1](
            workflow.registry._tools[name][0]
            and ToolInput(
                target_type=payload["target_type"],
                target_id=payload["target_id"],
                objective=payload["objective"],
            ),
            authorization,
        ) if name == "prepare_counter_offer" else type(
            "Result",
            (),
            {
                "succeeded": True,
                "data": {"mock": True},
                "error": None,
            },
        )()

    monkeypatch.setattr(
        workflow.registry,
        "execute",
        fake_registry_execute,
    )

    req = StartWorkflowRequest(
        objective="Negotiate purchase offer",
        target_type=TargetType.PURCHASE_OFFER,
        target_id=10,
    )

    result = workflow.run(
        user_id=1,
        role="OwnerAgent",
        req=req,
        authorization="Bearer test",
    )

    assert result.status == WorkflowStatus.AWAITING_APPROVAL
    assert len(result.approvals) == 1
    assert result.approvals[0].status == ApprovalStatus.PENDING

    # Critical safety assertion:
    assert "execute_counter_offer" not in executed_tools


# ---------------------------------------------------------
# Only OwnerAgent can decide high-impact approval
# ---------------------------------------------------------

def test_non_owner_agent_cannot_approve(monkeypatch):
    fake_record = {
        "id": 1,
        "workflow_id": "wf-1",
        "initiated_by_user_id": 1,
        "initiated_by_role": "OwnerAgent",
        "objective": "Negotiate purchase offer",
        "target_type": "PurchaseOffer",
        "target_id": 10,
        "status": "AwaitingApproval",
        "plan_json": None,
        "steps_json": "[]",
        "tool_calls_json": "[]",
        "approvals_json": """
        [{
            "id": 1,
            "action_name": "ExecuteProposedTransactionAction",
            "payload": {
                "action_payload": {
                    "offerAmount": 25000000
                }
            },
            "reason": "Human approval required",
            "status": "Pending",
            "decided_by_user_id": null,
            "decision_comment": null,
            "requested_at": "2026-10-07T10:00:00+00:00",
            "decided_at": null
        }]
        """,
        "final_outcome_json": None,
        "error": None,
        "created_at": "2026-10-07T10:00:00+00:00",
        "updated_at": "2026-10-07T10:00:00+00:00",
        "completed_at": None,
    }

    monkeypatch.setattr(
        workflow,
        "get",
        lambda workflow_id: fake_record,
    )

    decision = ApprovalDecisionRequest(
        decision=ApprovalStatus.APPROVED,
        comment="Approve",
    )

    with pytest.raises(
        PermissionError,
        match="Only an authorized OwnerAgent",
    ):
        workflow.decide(
            workflow_id="wf-1",
            approval_id=1,
            user_id=2,
            role="BuyerRenter",
            req=decision,
            authorization="Bearer test",
        )


# ---------------------------------------------------------
# Purchase amount validation
# ---------------------------------------------------------

def test_purchase_counter_offer_rejects_negative_amount():
    inp = CounterOfferInput(
        target_type="PurchaseOffer",
        target_id=10,
        objective="Execute counter offer",
        proposal={
            "action_payload": {
                "offerAmount": -5000,
                "conditions": "Test",
            }
        },
    )

    result = execute_counter_offer(
        inp,
        authorization="Bearer test",
    )

    assert result.succeeded is False
    assert "must be a positive number" in result.error


# ---------------------------------------------------------
# Rental duration boundary validation
# ---------------------------------------------------------

def test_rental_counter_offer_rejects_invalid_duration():
    inp = CounterOfferInput(
        target_type="RentalApplication",
        target_id=20,
        objective="Execute rental counter offer",
        proposal={
            "action_payload": {
                "monthlyRent": 100000,
                "moveInDate": "2026-11-01",
                "durationMonths": 121,
                "conditions": "Test",
            }
        },
    )

    result = execute_counter_offer(
        inp,
        authorization="Bearer test",
    )

    assert result.succeeded is False
    assert "between 1 and 120" in result.error


# ---------------------------------------------------------
# Execution requires authorization
# ---------------------------------------------------------

def test_counter_offer_execution_requires_authorization():
    inp = CounterOfferInput(
        target_type="PurchaseOffer",
        target_id=10,
        objective="Execute counter offer",
        proposal={
            "action_payload": {
                "offerAmount": 25000000,
                "conditions": "Test",
            }
        },
    )

    result = execute_counter_offer(
        inp,
        authorization=None,
    )

    assert result.succeeded is False
    assert "Authorization token is required" in result.error