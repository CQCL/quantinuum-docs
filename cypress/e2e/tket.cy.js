const checkThatNavBarExists = () => {
  cy.get('nav').contains(/tket/i).parent().parent().within(() => {
    cy.contains(/tket/i)
  })
}

const extensions = [
  "pytket-quantinuum", "pytket-azure", "pytket-qujax", "pytket-braket", "pytket-cutensornet", "pytket-qir", "pytket-qiskit", "pytket-iqm", "pytket-pennylane", "pytket-projectq", "pytket-pyquil", "pytket-pysimplex", "pytket-pyzx", "pytket-cirq", "pytket-qulacs", "pytket-stim"
]

describe('E2E Tests', () => {
  it('can view / (landing page)', () => {
    cy.visit('/tket/')
    checkThatNavBarExists()
    cy.contains(/The Universal Quantum Toolkit/i)
    cy.contains(/pip install pytket/i)
    cy.contains(/build/i)
    cy.contains(/compile/i)
    cy.contains(/run/i)
  })

  it("can view dropdown menu / (landing page navbar)", {
    retries: {
      runMode: 10,
      openMode: 10
    }
  }, () => {
    cy.visit('/tket/')
    checkThatNavBarExists()
    cy.contains('button', 'TKET').click();
    cy.contains(/Quantum computing toolkit and optimizing compiler/i).should("be.visible")
    cy.contains(/API Docs/i).should("be.visible")
    cy.contains(/Blog/i).should("be.visible")
    cy.contains(/User Guide/i).should("be.visible")
  })

  it('inspect api-docs from dropdown', {
    retries: {
      runMode: 10,
      openMode: 10
    }
  },() => {
    cy.visit('/tket/')
    checkThatNavBarExists()
    cy.contains('button', 'TKET').click();
    cy.contains(/API Docs/i).should("be.visible").click()
    cy.contains(/pytket is a python module for interfacing with tket/i)
  })

  it('inspect user-guide from dropdown', {
    retries: {
      runMode: 10,
      openMode: 10
    }
  },() => {
    cy.visit('/tket/')
    checkThatNavBarExists()
    cy.contains('button', 'TKET').click();
    cy.contains(/User Guide/i).should("be.visible").click()
    cy.contains(/getting started/i)
  })

  it('inspect blog from dropdown', {
    retries: {
      runMode: 20,
      openMode: 20
    }
  },() => {
    cy.visit('/tket/')
    checkThatNavBarExists()
    cy.contains('button', 'TKET').click();
    cy.contains(/Blog/i).should("be.visible").click()
    cy.contains(/tket developer blog/i)
  })

  it('can view /blog', () => {
    cy.visit('/tket/blog/')
    checkThatNavBarExists()
    cy.contains(/tket developer blog/i)
  })


  it('can view /extensions/{extension_name}', () => {
    extensions.forEach(extension => {
      cy.visit(`/tket/extensions/${extension}/`)
      checkThatNavBarExists()
      cy.contains(extension)
    })
  })

  it('can view /api-docs', () => {
    cy.visit('/tket/api-docs/')
    checkThatNavBarExists()
    cy.contains(/pytket is a python module for interfacing with tket/i)
  })

  it.skip('can link to root docs page from tket api-docs', () => {
  cy.visit('/tket/api-docs/')
  cy.findByLabelText(/quantinuum documentation/i).click()
  cy.origin('https://docs.quantinuum.com', () => {
    cy.contains(/technical documentation/i)
  })})
})
