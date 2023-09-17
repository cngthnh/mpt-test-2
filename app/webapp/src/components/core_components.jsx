/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";

function OnboardingComponent({ onSubmit }) {
  return (
    <div>
      <Directions>
        This component only renders if you have chosen to assign an onboarding
        qualification for your task. Click the button to move on to the main
        task.
      </Directions>
      <div
        style={{
          width: "100%",
          padding: "1.5rem 0",
          display: "flex",
          alignItems: "center",
          flexDirection: "column",
        }}
      >
        <button
          className="button is-success"
          style={{ width: "fit-content", marginBottom: "0.65rem" }}
          onClick={() => onSubmit({ success: true })}
        >
          Move to Main Task
        </button>
        <button
          className="button is-danger"
          style={{ width: "fit-content" }}
          onClick={() => onSubmit({ success: false })}
        >
          Get Blocked
        </button>
      </div>
    </div>
  );
}

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <section className="hero is-light" data-cy="directions-container">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">{children}</p>
        </div>
      </div>
    </section>
  );
}

function SimpleFrontend({ taskData, isOnboarding, onSubmit, onError }) {
  const data = { success: true };
  return (
    <div style={{ padding: "50px" }}>
      <button className="btn btn-outline" onClick={() => {
        onSubmit(data);
      }}>Button</button>
      Click this button to submit sample data.
    </div>
  );
}

export { LoadingScreen, SimpleFrontend as BaseFrontend, OnboardingComponent };
