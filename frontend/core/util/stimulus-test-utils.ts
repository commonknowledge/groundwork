import {
  Application,
  Controller,
  ControllerConstructor,
} from "@hotwired/stimulus";
import {
  BoundFunctions,
  getQueriesForElement,
  queries,
} from "@testing-library/dom";

/**
 * Configuration object for a test fixture
 */
export interface TestFixtureOpts {
  /** An html string binding the controller(s) to be tested */
  html: string;

  /**
   * List of controller classes made available to the test fixture.
   *
   * The identifier for the controller is derived from the classname – it is the lowercase version of the classname,
   * with any trailing 'controller' removed.
   *
   * For example:
   *  - `HelloWorldController` would be referenced via the attribute `data-controller="helloworld"`
   *  - `Map` would be referenced via the attribute `data-controller="map"`
   */
  controllers: ControllerConstructor[];
}

/**
 * Test fixture binding `@testing-library/dom`'s [queries](https://testing-library.com/docs/queries/about)
 * to a rendered stimulus application.
 */
export interface TestFixture extends BoundFunctions<typeof queries> {
  /** The stimulus application */
  application: Application;

  /**
   * Given a controller class and a test id (attached using `data-test-id`), return the matching controller instance.
   * Throws if the element is not found or no controller is registered.
   *
   * @param controller Any controller class
   * @param elementOrTestId Either the element the controller is attached to or its test id
   * @returns The instance of `controller` bound to the element.
   */
  getController<T extends Controller>(
    controller: new (...args: any[]) => T,
    elementOrTestId: string | Element
  ): T;
}

/**
 *
 *
 * @param param0 `TestFixtureOpts` object configuring the test application.
 * @returns A `TestFixture` instance wrapping a test application.
 */
export const createTestFixture = async ({
  html,
  controllers,
}: TestFixtureOpts): Promise<TestFixture> => {
  // Create an html element containg the test fixture's html
  const testCtx = document.createElement("body");
  testCtx.innerHTML = html;

  // Create a new stimulus application and register the test controllers.
  const application = Application.start(testCtx);
  for (const controller of controllers) {
    application.register(getTestControllerIdentifier(controller), controller);
  }

  // Allow Stimulus' mutation observers to fire at the end of the event loop so that it binds the controllers
  await Promise.resolve(setTimeout);

  // Combine testing-library's queries with some additional utils to create the fixture
  const boundQueries = getQueriesForElement(testCtx, queries);
  return Object.assign(boundQueries, {
    getController<T extends Controller>(
      controller: new (...args: any[]) => T,
      elementOrTestId: string | Element
    ) {
      const el =
        typeof elementOrTestId === "string"
          ? boundQueries.getByTestId(elementOrTestId)
          : elementOrTestId;

      const identifier = getTestControllerIdentifier(controller);
      const instance = application.getControllerForElementAndIdentifier(
        el,
        identifier
      );
      if (!instance) {
        throw Error(
          `No controller with identifier ${identifier} found on element with testid: ${elementOrTestId}`
        );
      }

      return instance as T;
    },
    application,
  });
};

/**
 * Given a controller class, return the identifier used to register it.
 *
 * @param controller Any controller class
 * @returns The identifier that the controller is registered with
 */
export const getTestControllerIdentifier = (
  controller: ControllerConstructor
) => controller.name.toLowerCase().replace(/controller$/, "");

export const customEvent = (detail: any) =>
  new CustomEvent("SomeEventType", { detail });
